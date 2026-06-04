-- vista schema. Single SQLite file. Designed for browsing in Datasette
-- and for ad-hoc SQL mining via `sqlite3 data/papers.db`.

CREATE TABLE IF NOT EXISTS papers (
    id              TEXT PRIMARY KEY,           -- OpenAlex work ID (Wxxxxxx)
    doi             TEXT,
    arxiv_id        TEXT,
    title           TEXT NOT NULL,
    authors_json    TEXT,                       -- JSON array of {name, orcid?}
    year            INTEGER,
    venue           TEXT,
    venue_id        TEXT,
    abstract        TEXT,
    cited_by_count  INTEGER,
    field           TEXT NOT NULL,              -- ml | ai | stats | ransomware
    track           TEXT NOT NULL,              -- recent | legacy | seed
    oa_url          TEXT,
    pdf_url         TEXT,
    pdf_path        TEXT,
    discovered_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    fetched_at      TEXT,
    raw_json        TEXT
);

CREATE INDEX IF NOT EXISTS idx_papers_field        ON papers(field);
CREATE INDEX IF NOT EXISTS idx_papers_track        ON papers(track);
CREATE INDEX IF NOT EXISTS idx_papers_year         ON papers(year);
CREATE INDEX IF NOT EXISTS idx_papers_cited_by     ON papers(cited_by_count);

-- Raw section text extracted from PDF.
CREATE TABLE IF NOT EXISTS sections (
    paper_id        TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    section_type    TEXT NOT NULL,              -- future_work | limitations | conclusion | discussion
    heading         TEXT,                       -- the actual heading we matched
    content         TEXT,
    method          TEXT,                       -- regex | grobid | manual
    extracted_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (paper_id, section_type)
);

-- Structured research directions distilled by the LLM analyzer.
CREATE TABLE IF NOT EXISTS directions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id        TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    direction       TEXT NOT NULL,              -- the direction itself, one sentence
    rationale       TEXT,                       -- why the paper suggests it
    quote           TEXT,                       -- supporting quote from the paper
    field_tags_json TEXT,                       -- JSON array of fine-grained tags
    feasibility     TEXT,                       -- low | medium | high
    novelty         TEXT,                       -- low | medium | high
    dependencies    TEXT,                       -- prerequisites or assumptions
    user_status     TEXT DEFAULT 'open',        -- open | interesting | started | abandoned
    user_notes      TEXT,
    analyzed_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_directions_paper ON directions(paper_id);
CREATE INDEX IF NOT EXISTS idx_directions_status ON directions(user_status);

-- One row per pipeline run, for provenance.
CREATE TABLE IF NOT EXISTS runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at     TEXT,
    config_json     TEXT,
    notes           TEXT
);

-- A view for the common browsing query.
CREATE VIEW IF NOT EXISTS v_directions_full AS
SELECT
    d.id            AS direction_id,
    d.direction,
    d.rationale,
    d.feasibility,
    d.novelty,
    d.user_status,
    d.field_tags_json,
    p.id            AS paper_id,
    p.title         AS paper_title,
    p.year,
    p.venue,
    p.field,
    p.track,
    p.cited_by_count,
    p.doi,
    p.arxiv_id,
    p.oa_url
FROM directions d
JOIN papers p ON p.id = d.paper_id;
