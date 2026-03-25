-- Capstone Seed: Music Catalog
-- Tables: genres, artists, albums, tracks

CREATE TABLE IF NOT EXISTS genres (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS artists (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  name    TEXT NOT NULL,
  country TEXT
);

CREATE TABLE IF NOT EXISTS albums (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  artist_id    INTEGER NOT NULL,
  year_released INTEGER,
  genre_id     INTEGER,
  FOREIGN KEY (artist_id) REFERENCES artists(id),
  FOREIGN KEY (genre_id)  REFERENCES genres(id)
);

CREATE TABLE IF NOT EXISTS tracks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  album_id     INTEGER NOT NULL,
  track_number INTEGER,
  duration_sec INTEGER,
  FOREIGN KEY (album_id) REFERENCES albums(id)
);

-- Genres
INSERT OR IGNORE INTO genres (id, name) VALUES (1, 'Jazz');
INSERT OR IGNORE INTO genres (id, name) VALUES (2, 'Soul');
INSERT OR IGNORE INTO genres (id, name) VALUES (3, 'Hip-Hop');
INSERT OR IGNORE INTO genres (id, name) VALUES (4, 'R&B');
INSERT OR IGNORE INTO genres (id, name) VALUES (5, 'Classical');
INSERT OR IGNORE INTO genres (id, name) VALUES (6, 'Electronic');
INSERT OR IGNORE INTO genres (id, name) VALUES (7, 'Rock');

-- Artists
INSERT OR IGNORE INTO artists (id, name, country) VALUES (1,  'Miles Davis',        'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (2,  'Aretha Franklin',    'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (3,  'Kendrick Lamar',     'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (4,  'Nina Simone',        'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (5,  'Daft Punk',          'France');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (6,  'Coltrane',           'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (7,  'Amy Winehouse',      'UK');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (8,  'Outkast',            'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (9,  'Billie Holiday',     'USA');
INSERT OR IGNORE INTO artists (id, name, country) VALUES (10, 'Radiohead',          'UK');

-- Albums
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (1,  'Kind of Blue',            1,  1959, 1);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (2,  'Bitches Brew',            1,  1970, 1);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (3,  'I Never Loved a Man',     2,  1967, 2);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (4,  'Lady Soul',               2,  1968, 2);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (5,  'good kid, m.A.A.d city', 3,  2012, 3);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (6,  'DAMN.',                   3,  2017, 3);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (7,  'I Put a Spell on You',    4,  1965, 2);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (8,  'Discovery',               5,  2001, 6);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (9,  'Random Access Memories', 5,  2013, 6);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (10, 'A Love Supreme',          6,  1965, 1);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (11, 'Back to Black',           7,  2006, 4);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (12, 'Stankonia',               8,  2000, 3);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (13, 'Lady in Satin',           9,  1958, 1);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (14, 'OK Computer',            10, 1997, 7);
INSERT OR IGNORE INTO albums (id, title, artist_id, year_released, genre_id)
VALUES (15, 'Kid A',                  10, 2000, 7);

-- Tracks (selected, duration in seconds)
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (1,  'So What',               1,  1, 562);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (2,  'Freddie Freeloader',    1,  2, 589);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (3,  'Blue in Green',         1,  3, 337);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (4,  'All Blues',             1,  4, 694);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (5,  'Flamenco Sketches',     1,  5, 566);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (6,  'Pharaoh''s Dance',      2,  1, 1194);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (7,  'Bitches Brew',          2,  2, 1614);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (8,  'I Never Loved a Man',   3,  1, 157);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (9,  'Respect',               3,  6, 147);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (10, 'Chain of Fools',        4,  2, 175);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (11, 'Backseat Freestyle',    5,  4, 213);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (12, 'Swimming Pools',        5,  8, 313);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (13, 'DNA.',                  6,  1, 186);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (14, 'HUMBLE.',               6,  8, 177);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (15, 'I Put a Spell on You',  7,  1, 192);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (16, 'Harder Better Faster',  8,  2, 224);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (17, 'Get Lucky',             9,  8, 369);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (18, 'Instant Crush',         9,  9, 337);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (19, 'A Love Supreme Pt. I',  10, 1, 499);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (20, 'Rehab',                 11, 1, 215);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (21, 'Back to Black',         11, 4, 241);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (22, 'Hey Ya!',               12, 6, 234);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (23, 'Ms. Jackson',           12, 3, 270);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (24, 'I''ll Be Seeing You',   13, 1, 183);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (25, 'Karma Police',          14, 4, 258);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (26, 'Paranoid Android',      14, 2, 383);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (27, 'Everything in Its Right Place', 15, 1, 261);
INSERT OR IGNORE INTO tracks (id, title, album_id, track_number, duration_sec)
VALUES (28, 'How to Disappear Completely',   15, 4, 336);
