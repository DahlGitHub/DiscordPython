CREATE TABLE IF NOT EXISTS league_patches (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    channel_id INTEGER,
    last_patch_url TEXT
);

CREATE TABLE IF NOT EXISTS enabled_extensions (
    extension TEXT PRIMARY KEY
);

DELETE FROM enabled_extensions WHERE extension = 'cogs.utils.reminder';

CREATE TABLE IF NOT EXISTS steam_promo_channels (
    guild_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    channel_id INTEGER NOT NULL,
    PRIMARY KEY (guild_id, kind)
);
CREATE TABLE IF NOT EXISTS steam_promo_posts (
    guild_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    app_id INTEGER NOT NULL,
    offer_end INTEGER NOT NULL,
    PRIMARY KEY (guild_id, kind, app_id, offer_end)
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

CREATE TABLE IF NOT EXISTS test_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS riot_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    puuid TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    tag TEXT NOT NULL,
    region TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bloons_favorite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    monkey_name TEXT NOT NULL,
    path1 INTEGER NOT NULL,
    path2 INTEGER NOT NULL,
    path3 INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bloons_key (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    key TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS todo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS crosspaths (
    monkey TEXT PRIMARY KEY,
    top TEXT,
    mid TEXT,
    bot TEXT,
    last_modified_by TEXT,
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS canvas_term (
    id INTEGER PRIMARY KEY DEFAULT 1,
    term_id INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS canvas_key (
    user_id INTEGER PRIMARY KEY,
    key TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS canvas_subscriptions (
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, course_id)
);

CREATE TABLE IF NOT EXISTS bot_presence (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL DEFAULT 'online',
    activity_type TEXT,
    message TEXT NOT NULL DEFAULT '',
    url TEXT
);
