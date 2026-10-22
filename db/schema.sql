-- ThermoTwin database schema (SQLite; portable to PostgreSQL with minor type changes).
-- Ownership: telemetry-service writes facilities, fridges, fridge_stock and readings;
-- alerts-service writes alert_events; vaccines is shared reference data.

CREATE TABLE IF NOT EXISTS facilities (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    taluka      TEXT,
    district    TEXT
);

CREATE TABLE IF NOT EXISTS fridges (
    id          TEXT PRIMARY KEY,
    facility_id TEXT NOT NULL REFERENCES facilities(id),
    label       TEXT NOT NULL,                       -- e.g. ILR-1
    cls         TEXT NOT NULL CHECK (cls IN ('ILR', 'DOMESTIC')),
    sort_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS vaccines (
    name             TEXT PRIMARY KEY,
    freeze_sensitive INTEGER NOT NULL CHECK (freeze_sensitive IN (0, 1)),
    note             TEXT
);

CREATE TABLE IF NOT EXISTS fridge_stock (
    fridge_id TEXT NOT NULL REFERENCES fridges(id),
    vaccine   TEXT NOT NULL REFERENCES vaccines(name),
    position  INTEGER NOT NULL DEFAULT 0,             -- display order
    PRIMARY KEY (fridge_id, vaccine)
);

-- One row per logger reading (every 10 minutes, as eVIN loggers record). temp_c is NULL for a missing reading.
CREATE TABLE IF NOT EXISTS readings (
    fridge_id TEXT NOT NULL REFERENCES fridges(id),
    source    TEXT NOT NULL,                          -- scenario name or upload batch
    tick      INTEGER NOT NULL,                       -- 10-minute index from the start of the source
    minute    INTEGER NOT NULL,
    temp_c    REAL,
    PRIMARY KEY (source, fridge_id, tick)
);

-- Guardian tier changes, written by alerts-service.
CREATE TABLE IF NOT EXISTS alert_events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    source    TEXT NOT NULL,
    fridge_id TEXT NOT NULL REFERENCES fridges(id),
    tick      INTEGER NOT NULL,
    tier      TEXT NOT NULL,
    kind      TEXT,
    message   TEXT
);

CREATE INDEX IF NOT EXISTS idx_readings_fridge ON readings (source, fridge_id, tick);
CREATE INDEX IF NOT EXISTS idx_alert_events_tick ON alert_events (source, tick);
