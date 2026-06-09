"""SQLite store. Idempotent writes; safe to re-run pipeline stages."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from vista.config import DB_PATH

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def connect(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA_PATH.read_text()
    conn.executescript(sql)
    conn.commit()


@dataclass
class Paper:
    id: str
    title: str
    field: str
    track: str
    doi: str | None = None
    arxiv_id: str | None = None
    authors_json: str | None = None
    year: int | None = None
    venue: str | None = None
    venue_id: str | None = None
    abstract: str | None = None
    cited_by_count: int | None = None
    oa_url: str | None = None
    pdf_url: str | None = None
    pdf_path: str | None = None
    fetched_at: str | None = None
    raw_json: str | None = None


@dataclass
class Section:
    paper_id: str
    section_type: str  # future_work | limitations | conclusion | discussion
    heading: str | None
    content: str
    method: str = "regex"


@dataclass
class Direction:
    paper_id: str
    direction: str
    rationale: str | None = None
    quote: str | None = None
    field_tags_json: str | None = None
    feasibility: str | None = None
    novelty: str | None = None
    dependencies: str | None = None


class Store:
    """Thin wrapper over sqlite. Methods are idempotent."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    @classmethod
    def open(cls, db_path: Path | str = DB_PATH) -> "Store":
        conn = connect(db_path)
        init_schema(conn)
        return cls(conn)

    @contextmanager
    def tx(self):
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # --- papers ----------------------------------------------------------

    def upsert_paper(self, p: Paper) -> None:
        d = asdict(p)
        cols = list(d.keys())
        placeholders = ",".join(":" + c for c in cols)
        # pdf_path/fetched_at are owned by the fetch stage; a re-discover (or a
        # live MCP cache_work) builds Papers with pdf_path=None and must not
        # reset fetch provenance on already-fetched rows.
        updates = ",".join(
            (f"{c}=COALESCE(excluded.{c}, papers.{c})"
             if c in ("pdf_path", "fetched_at")
             else f"{c}=excluded.{c}")
            for c in cols if c not in ("id", "discovered_at")
        )
        sql = (
            f"INSERT INTO papers ({','.join(cols)}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {updates}"
        )
        with self.tx():
            self.conn.execute(sql, d)

    def update_paper_pdf(self, paper_id: str, pdf_path: str | None, fetched_at: str | None) -> None:
        with self.tx():
            self.conn.execute(
                "UPDATE papers SET pdf_path=?, fetched_at=? WHERE id=?",
                (pdf_path, fetched_at, paper_id),
            )

    def papers(self, *, field: str | None = None, track: str | None = None,
               needs_pdf: bool = False, needs_extraction: bool = False,
               needs_analysis: bool = False) -> list[sqlite3.Row]:
        clauses, params = [], []
        if field:
            clauses.append("field = ?")
            params.append(field)
        if track:
            clauses.append("track = ?")
            params.append(track)
        if needs_pdf:
            clauses.append("pdf_path IS NULL AND (oa_url IS NOT NULL OR pdf_url IS NOT NULL)")
        if needs_extraction:
            clauses.append(
                "pdf_path IS NOT NULL AND id NOT IN (SELECT paper_id FROM sections)"
            )
        if needs_analysis:
            clauses.append(
                "id IN (SELECT paper_id FROM sections) "
                "AND id NOT IN (SELECT paper_id FROM directions)"
            )
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT * FROM papers{where} ORDER BY cited_by_count DESC NULLS LAST"
        return list(self.conn.execute(sql, params))

    def get_paper(self, paper_id: str) -> sqlite3.Row | None:
        return self.conn.execute("SELECT * FROM papers WHERE id=?", (paper_id,)).fetchone()

    # --- sections --------------------------------------------------------

    def upsert_sections(self, sections: Iterable[Section]) -> None:
        sql = (
            "INSERT INTO sections (paper_id, section_type, heading, content, method) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(paper_id, section_type) DO UPDATE SET "
            "heading=excluded.heading, content=excluded.content, method=excluded.method, "
            "extracted_at=CURRENT_TIMESTAMP"
        )
        rows = [(s.paper_id, s.section_type, s.heading, s.content, s.method) for s in sections]
        with self.tx():
            self.conn.executemany(sql, rows)

    def get_sections(self, paper_id: str) -> list[sqlite3.Row]:
        return list(self.conn.execute(
            "SELECT * FROM sections WHERE paper_id=? ORDER BY section_type",
            (paper_id,),
        ))

    # --- directions ------------------------------------------------------

    def replace_directions(self, paper_id: str, directions: Iterable[Direction]) -> None:
        with self.tx():
            self.conn.execute("DELETE FROM directions WHERE paper_id=?", (paper_id,))
            sql = (
                "INSERT INTO directions "
                "(paper_id, direction, rationale, quote, field_tags_json, "
                " feasibility, novelty, dependencies) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            self.conn.executemany(
                sql,
                [
                    (d.paper_id, d.direction, d.rationale, d.quote, d.field_tags_json,
                     d.feasibility, d.novelty, d.dependencies)
                    for d in directions
                ],
            )

    def get_directions(self, paper_id: str) -> list[sqlite3.Row]:
        return list(self.conn.execute(
            "SELECT * FROM directions WHERE paper_id=? ORDER BY id", (paper_id,)
        ))

    # --- runs ------------------------------------------------------------

    def begin_run(self, config: dict[str, Any]) -> int:
        with self.tx():
            cur = self.conn.execute(
                "INSERT INTO runs (config_json) VALUES (?)", (json.dumps(config),)
            )
            return cur.lastrowid or 0

    def finish_run(self, run_id: int, notes: str = "") -> None:
        with self.tx():
            self.conn.execute(
                "UPDATE runs SET finished_at=CURRENT_TIMESTAMP, notes=? WHERE id=?",
                (notes, run_id),
            )
