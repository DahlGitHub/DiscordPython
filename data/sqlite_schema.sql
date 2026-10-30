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

CREATE TABLE IF NOT EXISTS steam_users (
    guild_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    steam_id TEXT NOT NULL,
    wishlist TEXT NOT NULL DEFAULT '[]',
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS steam_channels (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS steam_games (
    guild_id INTEGER NOT NULL,
    app_id INTEGER NOT NULL,
    state TEXT NOT NULL,
    PRIMARY KEY (guild_id, app_id)
);
