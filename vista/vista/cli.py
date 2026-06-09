"""vista CLI."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from vista.config import (
    DB_PATH,
    DEFAULT_MODEL,
    FIELDS,
    OUT_DIR,
    PREMIUM_MODEL,
    RunConfig,
    SEEDS_DIR,
    ensure_dirs,
)
from vista.pipeline.analyze import run_analyze
from vista.pipeline.discover import run_discover
from vista.pipeline.extract import run_extract
from vista.pipeline.fetch import run_fetch
from vista.render.markdown import render_all
from vista.sources.bibtex import discover_bibs_in_repo, seed_from_bib
from vista.storage.db import Store

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Mine 'future work' sections from highly-cited papers.",
)
console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )


def _open_store() -> Store:
    ensure_dirs()
    return Store.open(DB_PATH)


def _build_config(
    fields: str,
    track: str,
    per_field: int,
    legacy_per_field: int,
    year_min_recent: int,
    require_oa: bool,
    model: str,
    skip_llm: bool,
) -> RunConfig:
    field_list = [f.strip() for f in fields.split(",") if f.strip()]
    for f in field_list:
        if f not in FIELDS:
            raise typer.BadParameter(f"unknown field: {f}; valid: {list(FIELDS)}")
    return RunConfig(
        fields=field_list,
        track=track,
        per_field_limit=per_field,
        legacy_per_field_limit=legacy_per_field,
        year_min_recent=year_min_recent,
        require_open_access=require_oa,
        model=model,
        skip_llm=skip_llm,
    )


@app.command()
def discover(
    fields: str = typer.Option("ml,ai,stats,ransomware", help="comma-separated"),
    track: str = typer.Option("recent", help="recent | legacy | both"),
    per_field: int = typer.Option(25),
    legacy_per_field: int = typer.Option(8),
    year_min_recent: int = typer.Option(2020),
    require_oa: bool = typer.Option(True, "--oa/--no-oa"),
    mailto: str = typer.Option("lex@metafunctor.com"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Discover papers via OpenAlex and store metadata."""
    _setup_logging(verbose)
    store = _open_store()
    cfg = _build_config(
        fields, track, per_field, legacy_per_field, year_min_recent,
        require_oa, DEFAULT_MODEL, skip_llm=True,
    )
    run_id = store.begin_run(cfg.__dict__)
    counts = run_discover(store, cfg, mailto=mailto)
    store.finish_run(run_id, notes=json.dumps({"discover": counts}))
    _print_counts("Discovered", counts)


@app.command()
def fetch(
    max_papers: int = typer.Option(0, help="0 = all"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Download PDFs for papers we have OA URLs for."""
    _setup_logging(verbose)
    store = _open_store()
    counts = run_fetch(store, max_papers=max_papers or None)
    _print_counts("Fetch", counts)


@app.command()
def extract(
    max_papers: int = typer.Option(0, help="0 = all"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Extract Future Work / Limitations / etc. sections from PDFs."""
    _setup_logging(verbose)
    store = _open_store()
    counts = run_extract(store, max_papers=max_papers or None)
    _print_counts("Extract", counts)


@app.command()
def analyze(
    max_papers: int = typer.Option(0, help="0 = all"),
    premium: bool = typer.Option(False, "--premium", help="use Fable instead of Sonnet"),
    model: str = typer.Option("", help="explicit model id; overrides --premium"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Run the LLM analyzer to extract structured directions."""
    _setup_logging(verbose)
    store = _open_store()
    chosen = model or (PREMIUM_MODEL if premium else DEFAULT_MODEL)
    counts = run_analyze(store, model=chosen, max_papers=max_papers or None)
    _print_counts(f"Analyze (model={chosen})", counts)


@app.command()
def render(
    out: Path = typer.Option(OUT_DIR, help="output directory"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Render the store to browseable markdown."""
    _setup_logging(verbose)
    store = _open_store()
    counts = render_all(store, out_dir=out)
    _print_counts("Render", counts)
    console.print(f"\n→ open [bold]{out / 'index.md'}[/bold]")


@app.command("seed-bib")
def seed_bib(
    paths: list[Path] = typer.Argument(..., help=".bib files or directories"),
    field: str = typer.Option(..., help="field to assign these seed papers"),
    track: str = typer.Option("seed"),
    mailto: str = typer.Option("lex@metafunctor.com"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Ingest .bib entries, resolve via OpenAlex, store with track=seed."""
    _setup_logging(verbose)
    store = _open_store()
    bib_files: list[Path] = []
    for p in paths:
        if p.is_dir():
            bib_files.extend(discover_bibs_in_repo([p]))
        elif p.exists():
            bib_files.append(p)
    if not bib_files:
        raise typer.BadParameter("no .bib files found")
    counts = seed_from_bib(store, bib_files, field=field, track=track, mailto=mailto)
    _print_counts(f"Seed ({len(bib_files)} bib files)", counts)


@app.command()
def status():
    """Show counts of papers, sections, directions per field/track."""
    store = _open_store()
    table = Table(title="vista store")
    table.add_column("field")
    table.add_column("track")
    table.add_column("papers", justify="right")
    table.add_column("with PDF", justify="right")
    table.add_column("with sections", justify="right")
    table.add_column("with directions", justify="right")
    rows = store.conn.execute(
        """
        SELECT
            p.field, p.track,
            COUNT(*) AS n_papers,
            SUM(p.pdf_path IS NOT NULL) AS n_pdf,
            SUM(EXISTS(SELECT 1 FROM sections s WHERE s.paper_id=p.id)) AS n_sec,
            SUM(EXISTS(SELECT 1 FROM directions d WHERE d.paper_id=p.id)) AS n_dir
        FROM papers p
        GROUP BY p.field, p.track
        ORDER BY p.field, p.track
        """
    ).fetchall()
    for r in rows:
        table.add_row(r["field"], r["track"], str(r["n_papers"]),
                      str(r["n_pdf"] or 0), str(r["n_sec"] or 0), str(r["n_dir"] or 0))
    console.print(table)


@app.command()
def pipeline(
    fields: str = typer.Option("ml,ai,stats,ransomware"),
    track: str = typer.Option("recent"),
    per_field: int = typer.Option(10),
    legacy_per_field: int = typer.Option(5),
    year_min_recent: int = typer.Option(2020),
    skip_analyze: bool = typer.Option(False, "--skip-analyze",
                                       help="run discover/fetch/extract only"),
    premium: bool = typer.Option(False, "--premium"),
    mailto: str = typer.Option("lex@metafunctor.com"),
    verbose: bool = typer.Option(False, "-v"),
):
    """Run discover -> fetch -> extract -> analyze -> render end-to-end."""
    _setup_logging(verbose)
    store = _open_store()
    cfg = _build_config(
        fields, track, per_field, legacy_per_field, year_min_recent,
        require_oa=True,
        model=PREMIUM_MODEL if premium else DEFAULT_MODEL,
        skip_llm=skip_analyze,
    )
    run_id = store.begin_run(cfg.__dict__)
    notes: dict = {}
    notes["discover"] = run_discover(store, cfg, mailto=mailto)
    _print_counts("Discovered", notes["discover"])
    notes["fetch"] = run_fetch(store)
    _print_counts("Fetch", notes["fetch"])
    notes["extract"] = run_extract(store)
    _print_counts("Extract", notes["extract"])
    if not skip_analyze:
        notes["analyze"] = run_analyze(store, model=cfg.model)
        _print_counts(f"Analyze (model={cfg.model})", notes["analyze"])
    notes["render"] = render_all(store)
    _print_counts("Render", notes["render"])
    store.finish_run(run_id, notes=json.dumps(notes))
    console.print(f"\n[green]Done.[/green] Open [bold]{OUT_DIR / 'index.md'}[/bold]")


def _print_counts(label: str, counts: dict) -> None:
    console.print(f"\n[bold]{label}:[/bold]")
    for k, v in counts.items():
        console.print(f"  {k}: {v}")


if __name__ == "__main__":
    app()
