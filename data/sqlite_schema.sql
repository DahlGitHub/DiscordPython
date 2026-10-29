CREATE TABLE IF NOT EXISTS league_patches (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    channel_id INTEGER,
    last_patch_url TEXT
);

CREATE TABLE IF NOT EXISTS embedfix_rules (
    name TEXT PRIMARY KEY,
    source TEXT NOT NULL UNIQUE,
    target TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS embedfix_channels (
    channel_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (channel_id, name),
    FOREIGN KEY (name) REFERENCES embedfix_rules (name)
        ON DELETE CASCADE
);

PRAGMA foreign_keys = ON;
