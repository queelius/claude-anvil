"""Configuration: fields, citation thresholds, model choices, paths."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from platformdirs import user_data_dir

REPO_ROOT = Path(__file__).resolve().parent.parent


# Data and output live in a user-scoped directory, not the package directory,
# so the catalog survives plugin updates and is shared between the CLI and
# the MCP server. Override with VISTA_DATA_DIR or VISTA_OUT_DIR for a project-
# local store (e.g., when running the CLI from a checkout).
def _path_from_env_or(default: Path, env: str) -> Path:
    val = os.environ.get(env)
    return Path(val).expanduser().resolve() if val else default


DEFAULT_DATA_DIR = Path(user_data_dir("vista", appauthor="queelius"))
DATA_DIR = _path_from_env_or(DEFAULT_DATA_DIR, "VISTA_DATA_DIR")
PDF_DIR = DATA_DIR / "pdfs"
TEXT_DIR = DATA_DIR / "text"
SEEDS_DIR = DATA_DIR / "seeds"
DB_PATH = DATA_DIR / "papers.db"
OUT_DIR = _path_from_env_or(DATA_DIR / "out", "VISTA_OUT_DIR")

USER_AGENT = "vista/0.1 (mailto:lex@metafunctor.com)"

# OpenAlex concept and source IDs (verified against api.openalex.org May 2026).
#
# Concepts are hierarchical; we filter by concept and (optionally) restrict to
# canonical venues. Some venues like IEEE S&P, CCS, AAAI year proceedings are
# fragmented across yearly sources in OpenAlex — rather than enumerate every
# year, we fall back to concept + keyword filtering for those fields.
# OpenAlex's `is_oa` flag is conservative — NeurIPS / ICML etc. papers aren't
# flagged OA even though arXiv mirrors exist. We therefore don't pre-filter by
# is_oa. Instead each field declares a `fulltext_filter` strategy:
#   - "arxiv-required": require the work to also live on arXiv (S4306400194).
#     Reliable PDF access. Best for ML/AI, where most major papers preprint.
#   - "venue-only":     filter by canonical venues only; accept paywalls and
#                       skip at fetch time.
#   - "any":            no extra filter; rely on whatever pdf_url / oa_url
#                       OpenAlex returns. Used for ransomware-style topical
#                       searches.
ARXIV_SOURCE_ID = "S4306400194"

FIELDS: dict[str, dict] = {
    "ml": {
        "label": "Machine Learning",
        "concept_ids": ["C119857082"],  # Machine learning
        "fulltext_filter": "arxiv-required",
        "min_citations_recent": 200,
        "min_citations_legacy": 2000,
    },
    "ai": {
        "label": "Artificial Intelligence",
        "concept_ids": ["C154945302"],  # Artificial intelligence
        "fulltext_filter": "arxiv-required",
        "min_citations_recent": 150,
        "min_citations_legacy": 1500,
    },
    "stats": {
        "label": "Statistics",
        "concept_ids": ["C105795698", "C160234255"],  # Statistics, Bayesian inference
        "venue_ids": [
            "S4394736638",  # JASA
            "S119757635",   # Annals of Statistics
            "S172180718",   # Biometrika
            "S145009937",   # JRSS-B
        ],
        "fulltext_filter": "venue-only",
        "min_citations_recent": 30,
        "min_citations_legacy": 300,
    },
    "ransomware": {
        "label": "Ransomware / Backup-based defenses",
        "concept_ids": ["C38652104"],  # Computer security
        # IEEE S&P, CCS are fragmented across year-specific sources; rely on
        # keyword search across abstracts/titles instead.
        "keywords": "ransomware",
        "fulltext_filter": "any",
        "min_citations_recent": 20,
        "min_citations_legacy": 100,
    },
}

# Anthropic model defaults. Per CLAUDE.md user notes, default to current Sonnet for cost,
# escalate to Fable for premium runs (--premium flag in CLI).
DEFAULT_MODEL = os.environ.get("FOLLOWUPS_MODEL", "claude-sonnet-4-6")
PREMIUM_MODEL = "claude-fable-5"


@dataclass
class RunConfig:
    fields: list[str] = field(default_factory=lambda: list(FIELDS.keys()))
    track: str = "recent"  # recent | legacy | both
    year_min_recent: int = 2020
    year_max_legacy: int = 2019
    year_min_legacy: int = 2005
    per_field_limit: int = 25
    legacy_per_field_limit: int = 8
    require_open_access: bool = True
    model: str = DEFAULT_MODEL
    skip_llm: bool = False  # set True to populate sections without invoking LLM yet
    extra_query: str | None = None


def ensure_dirs() -> None:
    for p in (DATA_DIR, PDF_DIR, TEXT_DIR, OUT_DIR, SEEDS_DIR):
        p.mkdir(parents=True, exist_ok=True)
