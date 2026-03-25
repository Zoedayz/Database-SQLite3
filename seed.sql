-- ============================================================
-- ZipCode Wilmington | SQL Exercises
-- library_seed.sql — SQLite3 seed file
--
-- Usage:
--   sqlite3 library.db
--   .read library_seed.sql
--   .tables
-- ============================================================


-- ------------------------------------------------------------
-- CLEANUP (safe to re-run)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS checkouts;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;
DROP TABLE IF EXISTS members;


-- ------------------------------------------------------------
-- TABLE: authors
-- ------------------------------------------------------------
CREATE TABLE authors (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  birth_year  INTEGER,
  nationality TEXT
);

INSERT INTO authors (name, birth_year, nationality) VALUES
  ('Toni Morrison',       1931, 'American'),
  ('George Orwell',       1903, 'British'),
  ('Gabriel García Márquez', 1927, 'Colombian'),
  ('Ursula K. Le Guin',   1929, 'American'),
  ('James Baldwin',       1924, 'American'),
  ('Octavia Butler',      1947, 'American'),
  ('Kazuo Ishiguro',      1954, 'British'),
  ('Chimamanda Ngozi Adichie', 1977, 'Nigerian'),
  ('Kurt Vonnegut',       1922, 'American'),
  ('Zadie Smith',         1975, 'British');


-- ------------------------------------------------------------
-- TABLE: books
-- ------------------------------------------------------------
CREATE TABLE books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT    NOT NULL,
  author_id      INTEGER,
  genre          TEXT,
  year_published INTEGER,
  pages          INTEGER,
  available      INTEGER DEFAULT 1,   -- 1 = yes, 0 = checked out
  FOREIGN KEY (author_id) REFERENCES authors(id)
);

INSERT INTO books (title, author_id, genre, year_published, pages, available) VALUES
  ('Beloved',                          1, 'Literary Fiction', 1987, 321, 1),
  ('The Bluest Eye',                   1, 'Literary Fiction', 1970, 206, 0),
  ('Song of Solomon',                  1, 'Literary Fiction', 1977, 337, 1),
  ('Nineteen Eighty-Four',             2, 'Dystopian',        1949, 328, 1),
  ('Animal Farm',                      2, 'Satire',           1945, 112, 0),
  ('Homage to Catalonia',              2, 'Nonfiction',       1938, 232, 1),
  ('One Hundred Years of Solitude',    3, 'Magical Realism',  1967, 417, 1),
  ('Love in the Time of Cholera',      3, 'Literary Fiction', 1985, 348, 1),
  ('The Left Hand of Darkness',        4, 'Science Fiction',  1969, 286, 0),
  ('The Dispossessed',                 4, 'Science Fiction',  1974, 341, 1),
  ('A Wizard of Earthsea',             4, 'Fantasy',          1968, 183, 1),
  ('Go Tell It on the Mountain',       5, 'Literary Fiction', 1953, 272, 1),
  ('Giovanni''s Room',                 5, 'Literary Fiction', 1956, 159, 0),
  ('The Fire Next Time',               5, 'Nonfiction',       1963, 106, 1),
  ('Kindred',                          6, 'Science Fiction',  1979, 264, 1),
  ('Parable of the Sower',             6, 'Dystopian',        1993, 295, 0),
  ('Bloodchild',                       6, 'Science Fiction',  1995, 208, 1),
  ('Never Let Me Go',                  7, 'Literary Fiction', 2005, 288, 1),
  ('The Remains of the Day',           7, 'Literary Fiction', 1989, 258, 0),
  ('Klara and the Sun',                7, 'Science Fiction',  2021, 307, 1),
  ('Purple Hibiscus',                  8, 'Literary Fiction', 2003, 307, 1),
  ('Half of a Yellow Sun',             8, 'Historical Fiction',2006, 433, 1),
  ('Americanah',                       8, 'Literary Fiction', 2013, 477, 0),
  ('Slaughterhouse-Five',              9, 'Satire',           1969, 215, 1),
  ('Cat''s Cradle',                    9, 'Satire',           1963, 287, 1),
  ('Breakfast of Champions',           9, 'Satire',           1973, 303, 0),
  ('White Teeth',                     10, 'Literary Fiction', 2000, 448, 1),
  ('On Beauty',                       10, 'Literary Fiction', 2005, 443, 1),
  ('NW',                              10, 'Literary Fiction', 2012, 304, 0);


-- ------------------------------------------------------------
-- TABLE: members
-- ------------------------------------------------------------
CREATE TABLE members (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  email       TEXT    UNIQUE NOT NULL,
  joined_year INTEGER
);

INSERT INTO members (name, email, joined_year) VALUES
  ('Alice Drummond',   'alice.drummond@email.com',   2019),
  ('Marcus Webb',      'marcus.webb@email.com',       2020),
  ('Priya Nair',       'priya.nair@email.com',        2021),
  ('Jordan Ellis',     'jordan.ellis@email.com',      2018),
  ('Sam Okonkwo',      'sam.okonkwo@email.com',       2022),
  ('Diana Flores',     'diana.flores@email.com',      2020),
  ('Tom Brannigan',    'tom.brannigan@email.com',     2023),
  ('Yuki Tanaka',      'yuki.tanaka@email.com',       2019),
  ('Cleo Marsh',       'cleo.marsh@email.com',        2021),
  ('Rafael Díaz',      'rafael.diaz@email.com',       2022);


-- ------------------------------------------------------------
-- TABLE: checkouts
-- (links members to books they have checked out)
-- ------------------------------------------------------------
CREATE TABLE checkouts (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id    INTEGER NOT NULL,
  book_id      INTEGER NOT NULL,
  checkout_date TEXT   NOT NULL,   -- stored as TEXT: 'YYYY-MM-DD'
  due_date      TEXT   NOT NULL,
  returned      INTEGER DEFAULT 0, -- 0 = not returned, 1 = returned
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (book_id)   REFERENCES books(id)
);

INSERT INTO checkouts (member_id, book_id, checkout_date, due_date, returned) VALUES
  (1,  2,  '2024-11-01', '2024-11-15', 1),
  (1,  5,  '2025-01-10', '2025-01-24', 0),
  (2,  9,  '2025-01-05', '2025-01-19', 1),
  (2,  13, '2025-02-01', '2025-02-15', 0),
  (3,  16, '2025-01-20', '2025-02-03', 0),
  (3,  19, '2024-12-01', '2024-12-15', 1),
  (4,  23, '2025-02-10', '2025-02-24', 0),
  (4,  26, '2025-01-15', '2025-01-29', 1),
  (5,  29, '2025-02-05', '2025-02-19', 0),
  (6,  2,  '2024-10-01', '2024-10-15', 1),
  (7,  5,  '2025-02-12', '2025-02-26', 0),
  (8,  9,  '2024-12-20', '2025-01-03', 1),
  (9,  13, '2025-01-28', '2025-02-11', 0),
  (10, 19, '2025-02-08', '2025-02-22', 0);


-- ------------------------------------------------------------
-- VERIFICATION
-- ------------------------------------------------------------
SELECT '--- Seed complete ---' AS status;
SELECT 'authors : ' || COUNT(*) AS row_counts FROM authors
UNION ALL
SELECT 'books   : ' || COUNT(*) FROM books
UNION ALL
SELECT 'members : ' || COUNT(*) FROM members
UNION ALL
SELECT 'checkouts: ' || COUNT(*) FROM checkouts;
