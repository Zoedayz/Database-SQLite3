#!/usr/bin/env python3
"""
SQLite3 Library — Interactive Terminal Tutor
Walks adult students through SQL fundamentals using sqlite3.
Usage: python3 tutor.py
"""

import os
import sys
import json
import sqlite3
import textwrap
import readline  # noqa: F401 — enables arrow-key history in input()

# ── ANSI color helpers ───────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RED    = "\033[31m"
BLUE   = "\033[34m"
MAGENTA = "\033[35m"
WHITE  = "\033[97m"

def c(text, *codes):
    return "".join(codes) + str(text) + RESET

def hr(char="─", width=70, colour=DIM):
    return c(char * width, colour)

def banner(text):
    line = "═" * 70
    print(c(line, BOLD + CYAN))
    print(c(f"  {text}", BOLD + CYAN))
    print(c(line, BOLD + CYAN))

def section(text):
    print(c(f"\n  {text}", BOLD + YELLOW))
    print(c("  " + "─" * (len(text) + 2), DIM))

def info(text):
    for line in text.splitlines():
        print(c(f"  {line}", WHITE))

def hint_text(text):
    print(c(f"  💡  {text}", CYAN))

def success(text):
    print(c(f"\n  ✔  {text}", GREEN + BOLD))

def error(text):
    print(c(f"\n  ✖  {text}", RED + BOLD))

def prompt_line():
    print()
    return input(c("  sqlite> ", BOLD + GREEN)).strip()

# ── Progress tracking ────────────────────────────────────────────────────────

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), ".progress.json")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed": []}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def mark_done(exercise_id, progress):
    if exercise_id not in progress["completed"]:
        progress["completed"].append(exercise_id)
    save_progress(progress)

# ── Database helpers ─────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def run_sql(conn, sql, quiet=False):
    """Execute one or more SQL statements; pretty-print results."""
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    any_rows = False
    for stmt in statements:
        try:
            cur = conn.execute(stmt)
            conn.commit()
            rows = cur.fetchall()
            if rows:
                any_rows = True
                _print_table(cur.description, rows)
            elif cur.rowcount > 0 and not quiet:
                success(f"{cur.rowcount} row(s) affected.")
            elif not quiet and not any_rows and not rows:
                print(c("  (no rows returned)", DIM))
        except sqlite3.Error as e:
            error(str(e))
            return False
    return True

def _print_table(description, rows):
    if not description:
        return
    col_names = [d[0] for d in description]
    col_widths = [len(n) for n in col_names]
    str_rows = []
    for row in rows:
        str_row = [str(v) if v is not None else "NULL" for v in row]
        str_rows.append(str_row)
        for i, val in enumerate(str_row):
            col_widths[i] = max(col_widths[i], len(val))

    sep = "  +" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header = "  |" + "|".join(
        c(f" {col_names[i]:<{col_widths[i]}} ", BOLD + CYAN)
        for i in range(len(col_names))
    ) + "|"
    print(sep)
    print(header)
    print(sep)
    for str_row in str_rows:
        row_str = "  |" + "|".join(
            f" {str_row[i]:<{col_widths[i]}} " for i in range(len(str_row))
        ) + "|"
        print(row_str)
    print(sep)
    print(c(f"  {len(rows)} row(s).", DIM))

def handle_dot_command(conn, cmd):
    """Emulate common sqlite3 CLI dot-commands."""
    parts = cmd.strip().split()
    name = parts[0].lower()

    if name == ".quit" or name == ".exit":
        print(c("\n  Goodbye! Keep practicing.\n", BOLD + CYAN))
        sys.exit(0)

    elif name == ".help":
        print(c("""
  Dot-commands available in this tutor:
    .tables             List all tables
    .schema [table]     Show CREATE statement(s)
    .databases          Show attached databases
    .mode column        (acknowledged — output is always column mode)
    .headers on/off     (acknowledged — headers are always shown)
    .nullvalue <str>    Set string for NULL display
    .read <file>        Execute SQL from a file
    .quit / .exit       Exit the tutor
    .help               Show this message
""", CYAN))

    elif name == ".tables":
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        rows = cur.fetchall()
        if rows:
            print("  " + "  ".join(r[0] for r in rows))
        else:
            print(c("  (no tables yet)", DIM))

    elif name == ".schema":
        table = parts[1] if len(parts) > 1 else None
        if table:
            cur = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;",
                (table,),
            )
        else:
            cur = conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name;"
            )
        rows = cur.fetchall()
        if rows:
            for row in rows:
                if row[0]:
                    print(c("  " + row[0], CYAN))
        else:
            print(c("  (nothing found)", DIM))

    elif name == ".databases":
        cur = conn.execute("PRAGMA database_list;")
        rows = cur.fetchall()
        _print_table(cur.description, rows)

    elif name in (".mode", ".headers", ".separator", ".nullvalue"):
        print(c(f"  ('{name}' acknowledged — formatting is handled by the tutor)", DIM))

    elif name == ".read":
        if len(parts) < 2:
            error("Usage: .read <filename>")
            return
        filepath = parts[1]
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.path.dirname(__file__), filepath)
        if not os.path.exists(filepath):
            error(f"File not found: {filepath}")
            return
        with open(filepath) as fh:
            sql = fh.read()
        print(c(f"  Reading {filepath} …", DIM))
        run_sql(conn, sql)

    else:
        print(c(f"  Unknown dot-command: {cmd}  (try .help)", YELLOW))

# ── Exercise definitions ─────────────────────────────────────────────────────

EXERCISES = [
    {
        "id": 1,
        "title": "What is a Database?",
        "concept": "Relational model, tables, rows, columns",
        "intro": """\
Welcome to Exercise 1!

A *relational database* stores data in tables — grids of rows and columns,
a bit like a spreadsheet.  Unlike a spreadsheet, the database enforces rules,
handles millions of rows efficiently, and lets multiple programs share the
same data safely.

A *row* (also called a record) is one entry.
A *column* (also called a field) is one attribute of that entry.
A *table* is the collection of all rows with the same columns.

In this tutor you will work with a small public-library database: library.db.

Let's explore the sqlite3 dot-commands first.  These are not SQL — they are
special commands understood by the sqlite3 shell (and this tutor).""",
        "tasks": [
            "Type  .databases  to see the attached database file.",
            "Type  .tables     to list all tables (none yet — that's OK).",
            "Type  .help       to browse available dot-commands.",
            "Type  .done       when you have tried all three.",
        ],
        "hints": [
            "Dot-commands start with a dot (.) and are not followed by a semicolon.",
            "Try each command one at a time and read the output carefully.",
        ],
        "reflection": [
            "What is a 'relation' in the relational model?",
            "Why use a database instead of a plain spreadsheet?",
            "What is the difference between a row and a record?",
        ],
        "setup": [],
    },
    {
        "id": 2,
        "title": "Creating Tables",
        "concept": "CREATE TABLE, data types (INTEGER, TEXT)",
        "intro": """\
Exercise 2 — Creating Tables

Before you can store data you need to define its *schema* — the structure of
your tables, their column names, and the data type of each column.

SQLite3 supports these core types:
  INTEGER   — whole numbers
  REAL      — floating-point numbers
  TEXT      — character strings
  BLOB      — raw binary data
  NULL      — the absence of a value

Every table should have a *primary key* — a column (or set of columns) that
uniquely identifies each row.  Using INTEGER PRIMARY KEY AUTOINCREMENT lets
SQLite assign IDs automatically.""",
        "tasks": [
            "Create the 'authors' table (copy the SQL below and press Enter).",
            "Create the 'books' table.",
            "Use .tables to confirm both tables exist.",
            "Use .schema authors and .schema books to inspect them.",
        ],
        "example_sql": """\
CREATE TABLE authors (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  birth_year  INTEGER
);

CREATE TABLE books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
        "hints": [
            "End every SQL statement with a semicolon (;).",
            "NOT NULL means the column must always have a value.",
            "AUTOINCREMENT means SQLite will fill in the id automatically.",
            "If you get 'table already exists', that's fine — it was set up for you.",
        ],
        "reflection": [
            "Why is 'id' an INTEGER instead of TEXT?",
            "What happens if you omit NOT NULL on a column?",
            "What other data types might a library database need?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
        ],
    },
    {
        "id": 3,
        "title": "Inserting Data",
        "concept": "INSERT INTO … VALUES",
        "intro": """\
Exercise 3 — Inserting Data

Now that the tables exist, let's populate them.  The INSERT INTO statement
adds a new row to a table.

Syntax:
  INSERT INTO table_name (col1, col2, …) VALUES (val1, val2, …);

You can omit a column if it has a default value or allows NULL.
The 'id' column is AUTOINCREMENT so we never provide it ourselves.""",
        "tasks": [
            "Insert at least 6 authors using the examples below.",
            "Insert at least 6 books.",
            "Try omitting a NOT NULL column (title) to see the error.",
            "Run  SELECT * FROM authors;  to verify your inserts.",
        ],
        "example_sql": """\
INSERT INTO authors (name, birth_year) VALUES ('Toni Morrison', 1931);
INSERT INTO authors (name, birth_year) VALUES ('George Orwell', 1903);
INSERT INTO authors (name, birth_year) VALUES ('James Baldwin', 1924);
INSERT INTO authors (name, birth_year) VALUES ('Octavia Butler', 1947);
INSERT INTO authors (name, birth_year) VALUES ('Ursula K. Le Guin', 1929);
INSERT INTO authors (name, birth_year) VALUES ('Zora Neale Hurston', 1891);

INSERT INTO books (title, genre, year_published) VALUES ('Beloved', 'Fiction', 1987);
INSERT INTO books (title, genre, year_published) VALUES ('Nineteen Eighty Four', 'Fiction', 1949);
INSERT INTO books (title, genre, year_published) VALUES ('Go Tell It on the Mountain', 'Fiction', 1953);
INSERT INTO books (title, genre, year_published) VALUES ('Kindred', 'Science Fiction', 1979);
INSERT INTO books (title, genre, year_published) VALUES ('The Left Hand of Darkness', 'Science Fiction', 1969);
INSERT INTO books (title, genre, year_published) VALUES ('Their Eyes Were Watching God', 'Fiction', 1937);
INSERT INTO books (title, genre, year_published) VALUES ('Animal Farm', 'Satire', 1945);
INSERT INTO books (title, genre, year_published) VALUES ('Parable of the Sower', 'Science Fiction', 1993);""",
        "hints": [
            "Text values must be wrapped in single quotes: 'like this'.",
            "If you see 'NOT NULL constraint failed', you forgot a required column.",
            "The semicolon is the statement terminator — don't forget it.",
        ],
        "reflection": [
            "What error do you get when you omit a NOT NULL column?",
            "Why don't we supply the 'id' value ourselves?",
            "What would happen if two INSERT statements had the same id?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 4,
        "title": "Querying Data",
        "concept": "SELECT, FROM, WHERE",
        "intro": """\
Exercise 4 — Querying Data

SELECT is the most important SQL statement.  It reads data from a table
without changing anything.

Syntax:
  SELECT col1, col2 FROM table_name;
  SELECT col1, col2 FROM table_name WHERE condition;
  SELECT * FROM table_name;   -- * means "all columns"

The WHERE clause filters which rows are returned.  Only rows where the
condition is TRUE are included in the result.""",
        "tasks": [
            "Select all columns from the books table.",
            "Select only the title and genre columns from books.",
            "Select books published after 1950.",
            "Select authors born before 1920.",
            "Select a specific author by name (pick any author from Exercise 3).",
        ],
        "example_sql": """\
-- All books
SELECT * FROM books;

-- Only title and genre
SELECT title, genre FROM books;

-- Books published after 1950
SELECT title, year_published FROM books WHERE year_published > 1950;

-- Authors born before 1920
SELECT name, birth_year FROM authors WHERE birth_year < 1920;

-- A specific author
SELECT * FROM authors WHERE name = 'Toni Morrison';""",
        "hints": [
            "Use single quotes around text values in WHERE: WHERE name = 'Orwell'",
            "SELECT * is convenient but in real apps you usually name each column.",
            "SQL is case-insensitive for keywords: SELECT = select = Select.",
            "Column names and table names ARE case-sensitive in SQLite.",
        ],
        "reflection": [
            "What is the difference between SELECT * and SELECT title, genre?",
            "Why should you prefer named columns over * in production code?",
            "What happens if the WHERE condition matches no rows?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 5,
        "title": "Filtering and Sorting",
        "concept": "WHERE operators, ORDER BY, LIMIT",
        "intro": """\
Exercise 5 — Filtering and Sorting

You can combine multiple conditions in WHERE using AND / OR, and use ORDER BY
to sort results.  LIMIT caps how many rows are returned.

Comparison operators:  =  !=  >  >=  <  <=
Pattern matching:      LIKE  (% matches any sequence, _ matches one character)
Examples:
  WHERE genre = 'Fiction'
  WHERE year_published BETWEEN 1940 AND 1960
  WHERE title LIKE '%the%'       -- title contains "the"
  WHERE genre IS NULL            -- genre has no value""",
        "tasks": [
            "Select all Fiction books, sorted by year_published (newest first).",
            "Select the 3 most recently published books.",
            "Find all books whose title contains the word 'the' (case-insensitive).",
            "Find authors born between 1900 and 1930.",
            "Select books that are either 'Fiction' OR 'Satire'.",
        ],
        "example_sql": """\
-- Fiction books sorted newest first
SELECT title, year_published
FROM books
WHERE genre = 'Fiction'
ORDER BY year_published DESC;

-- 3 most recent books
SELECT title FROM books ORDER BY year_published DESC LIMIT 3;

-- Titles containing "the" (LIKE is case-insensitive in SQLite by default for ASCII)
SELECT title FROM books WHERE title LIKE '%the%';

-- Authors born 1900–1930
SELECT name, birth_year FROM authors
WHERE birth_year >= 1900 AND birth_year <= 1930
ORDER BY birth_year;

-- Fiction or Satire
SELECT title, genre FROM books WHERE genre = 'Fiction' OR genre = 'Satire';""",
        "hints": [
            "DESC = descending (highest first).  ASC = ascending (lowest first, the default).",
            "LIMIT always comes after ORDER BY.",
            "LIKE '%word%' — the % signs are wildcards meaning 'anything here'.",
            "AND has higher precedence than OR; use parentheses when mixing them.",
        ],
        "reflection": [
            "What is the difference between ORDER BY year ASC and ORDER BY year DESC?",
            "What does LIMIT do when fewer rows match than the limit?",
            "When would you use LIKE instead of =?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 6,
        "title": "Updating Records",
        "concept": "UPDATE … SET … WHERE",
        "intro": """\
Exercise 6 — Updating Records

UPDATE modifies existing rows.  Always use a WHERE clause to target only the
rows you want to change.

⚠  WARNING: An UPDATE without WHERE changes EVERY row in the table.
   Best practice: write the SELECT first to confirm which rows you'll change,
   then write the UPDATE.

Syntax:
  UPDATE table_name SET col = new_value WHERE condition;
  UPDATE table_name SET col1 = v1, col2 = v2 WHERE condition;""",
        "tasks": [
            "First SELECT books WHERE id = 2 to see the current title.",
            "Fix the title: UPDATE books SET title = 'Nineteen Eighty-Four' WHERE id = 2;",
            "SELECT that row again to confirm the change.",
            "Set genre = 'Unknown' for any books where genre IS NULL.",
        ],
        "example_sql": """\
-- Step 1: confirm what you are about to change
SELECT id, title FROM books WHERE id = 2;

-- Step 2: make the change
UPDATE books SET title = 'Nineteen Eighty-Four' WHERE id = 2;

-- Step 3: verify
SELECT id, title FROM books WHERE id = 2;

-- Update all NULL genres
UPDATE books SET genre = 'Unknown' WHERE genre IS NULL;""",
        "hints": [
            "Always SELECT before UPDATE to confirm which rows will change.",
            "IS NULL is the correct syntax — don't write = NULL.",
            "You can update multiple columns at once: SET col1 = v1, col2 = v2",
        ],
        "reflection": [
            "What would happen if you ran UPDATE books SET genre = 'Fiction'; (no WHERE)?",
            "How do you undo an accidental UPDATE in SQLite3?",
            "Why is it safer to UPDATE by id rather than by name?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 7,
        "title": "Deleting Records",
        "concept": "DELETE FROM … WHERE",
        "intro": """\
Exercise 7 — Deleting Records

DELETE removes rows from a table permanently (unless you are in a transaction
you can roll back).  Just like UPDATE, always use WHERE.

⚠  DELETE FROM table_name;   ← deletes EVERY row — use with extreme caution.

The recommended workflow:
  1. SELECT to see what you are about to delete.
  2. DELETE with the same WHERE clause.
  3. SELECT again to confirm the row is gone.""",
        "tasks": [
            "Insert a 'bad' book record that you will then delete.",
            "SELECT that record to confirm it exists.",
            "DELETE it using its id.",
            "SELECT again to confirm it is gone.",
        ],
        "example_sql": """\
-- Insert a bad record
INSERT INTO books (title, genre, year_published) VALUES ('Bad Test Record', 'Test', 2000);

-- Check it was created (note its id)
SELECT * FROM books ORDER BY id DESC LIMIT 3;

-- Delete it (replace 9 with the actual id you saw)
DELETE FROM books WHERE id = 9;

-- Confirm it is gone
SELECT * FROM books ORDER BY id DESC LIMIT 3;""",
        "hints": [
            "Use SELECT first — confirm the exact id before you DELETE.",
            "There is no UNDO in SQLite3 once you commit.  Be careful!",
            "DELETE only removes rows; the table itself remains.",
        ],
        "reflection": [
            "What is the difference between DELETE FROM books WHERE id=5 and DROP TABLE books?",
            "Why is it safer to delete by id rather than by name or title?",
            "What is a transaction, and how could it protect you from accidental deletes?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 8,
        "title": "Primary Keys and Uniqueness",
        "concept": "PRIMARY KEY, AUTOINCREMENT, UNIQUE constraint",
        "intro": """\
Exercise 8 — Primary Keys and Uniqueness

A PRIMARY KEY uniquely identifies every row.  A UNIQUE constraint prevents
duplicate values in a column even if it is not the primary key.

Surrogate key: an artificial id column (usually AUTOINCREMENT).
Natural key:   a real-world value (email, ISBN, etc.).

Surrogate keys are preferred because:
  • Natural keys can change (people change email addresses).
  • Natural keys may not exist for every row.
  • Integer comparisons are faster than string comparisons.""",
        "tasks": [
            "Create a 'members' table with a UNIQUE email column.",
            "Insert two members with different emails — this should succeed.",
            "Try inserting two members with the same email — observe the error.",
            "Use .schema members to inspect the constraint.",
        ],
        "example_sql": """\
CREATE TABLE members (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name  TEXT NOT NULL
);

-- These should both succeed
INSERT INTO members (email, name) VALUES ('alice@example.com', 'Alice');
INSERT INTO members (email, name) VALUES ('bob@example.com',   'Bob');

-- This should fail with UNIQUE constraint error
INSERT INTO members (email, name) VALUES ('alice@example.com', 'Alice Again');

-- Inspect the table
SELECT * FROM members;""",
        "hints": [
            "The error for a duplicate unique value is: UNIQUE constraint failed",
            "AUTOINCREMENT guarantees ids are never reused, even after deletes.",
            "A table can have only one PRIMARY KEY but many UNIQUE columns.",
        ],
        "reflection": [
            "Why use an id column instead of email as the primary key?",
            "What would happen to existing data if you added UNIQUE to an existing column that already has duplicates?",
            "Name a real-world example where a natural key makes sense.",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 9,
        "title": "Aggregate Functions",
        "concept": "COUNT, SUM, AVG, MIN, MAX",
        "intro": """\
Exercise 9 — Aggregate Functions

Aggregate functions compute a single summary value from a set of rows.

  COUNT(*)         — total number of rows
  COUNT(column)    — rows where column is not NULL
  SUM(column)      — sum of all values
  AVG(column)      — arithmetic mean
  MIN(column)      — smallest value
  MAX(column)      — largest value

You can use AS to give the result a readable name:
  SELECT COUNT(*) AS total_books FROM books;""",
        "tasks": [
            "Count the total number of books in the library.",
            "Find the average birth year of all authors.",
            "Find the earliest and latest year_published in books.",
            "Count how many books have a non-NULL genre.",
            "Challenge: count how many books are in each genre. (Hint: see Exercise 10)",
        ],
        "example_sql": """\
-- Total books
SELECT COUNT(*) AS total_books FROM books;

-- Average author birth year
SELECT AVG(birth_year) AS avg_birth_year FROM authors;

-- Year range of books
SELECT MIN(year_published) AS earliest,
       MAX(year_published) AS latest
FROM books;

-- Books with a non-NULL genre
SELECT COUNT(genre) AS books_with_genre FROM books;""",
        "hints": [
            "COUNT(*) counts all rows including NULLs; COUNT(col) skips NULLs.",
            "AVG ignores NULL values automatically.",
            "You can use AS to rename any column in the result set.",
        ],
        "reflection": [
            "What is the difference between COUNT(*) and COUNT(genre)?",
            "What would AVG return if all values in the column were NULL?",
            "When would you use SUM versus COUNT?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 10,
        "title": "Grouping Data",
        "concept": "GROUP BY, HAVING",
        "intro": """\
Exercise 10 — Grouping Data

GROUP BY collapses multiple rows that share the same value into one group, so
you can compute aggregates per group (e.g. count per genre).

HAVING is the GROUP BY equivalent of WHERE.  Key distinction:
  WHERE   — filters individual rows BEFORE grouping
  HAVING  — filters groups AFTER grouping (can reference aggregate functions)

Typical pattern:
  SELECT col, COUNT(*) AS n
  FROM table
  WHERE <optional row filter>
  GROUP BY col
  HAVING n > 1
  ORDER BY n DESC;""",
        "tasks": [
            "Count the number of books in each genre.",
            "Show only genres that have more than 1 book.",
            "Find the oldest author birth year per first letter of their name. (challenge)",
            "Count books published per decade using year_published / 10 * 10.",
        ],
        "example_sql": """\
-- Books per genre
SELECT genre, COUNT(*) AS total
FROM books
GROUP BY genre
ORDER BY total DESC;

-- Only genres with more than 1 book
SELECT genre, COUNT(*) AS total
FROM books
GROUP BY genre
HAVING total > 1;

-- Books per decade
SELECT (year_published / 10) * 10 AS decade,
       COUNT(*) AS total
FROM books
GROUP BY decade
ORDER BY decade;""",
        "hints": [
            "Every column in SELECT must either be in GROUP BY or wrapped in an aggregate.",
            "HAVING comes after GROUP BY and before ORDER BY.",
            "You can GROUP BY an expression, not just a column name.",
        ],
        "reflection": [
            "Why can't you use WHERE to filter on COUNT(*)?",
            "What does GROUP BY do when there are NULL values in the grouped column?",
            "Write the query without GROUP BY. What do you get? Why is GROUP BY needed?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 11,
        "title": "Joins",
        "concept": "Foreign keys, INNER JOIN, LEFT JOIN",
        "intro": """\
Exercise 11 — Joins

A foreign key is a column in one table that references the primary key of
another table.  Joins combine rows from two tables based on a matching column.

INNER JOIN  — returns only rows where the match exists in BOTH tables.
LEFT JOIN   — returns ALL rows from the left table; right-side columns are NULL
              when no match exists.

We will link each book to its author by adding an author_id column to books
(using ALTER TABLE), then populate it, then write join queries.""",
        "tasks": [
            "Add an author_id column to the books table.",
            "Update books to set their author_id (see examples).",
            "Write an INNER JOIN to show each book title with its author name.",
            "Write a LEFT JOIN to find books that have no author assigned yet.",
        ],
        "example_sql": """\
-- Add the foreign key column
ALTER TABLE books ADD COLUMN author_id INTEGER;

-- Link books to authors by id
UPDATE books SET author_id = 1 WHERE title = 'Beloved';
UPDATE books SET author_id = 2 WHERE title LIKE '%Eighty%';
UPDATE books SET author_id = 3 WHERE title LIKE '%Mountain%';
UPDATE books SET author_id = 4 WHERE title = 'Kindred';
UPDATE books SET author_id = 4 WHERE title LIKE '%Sower%';
UPDATE books SET author_id = 5 WHERE title LIKE '%Darkness%';
UPDATE books SET author_id = 6 WHERE title LIKE '%Watching%';
UPDATE books SET author_id = 2 WHERE title = 'Animal Farm';

-- INNER JOIN: only books that have an author
SELECT books.title, authors.name AS author
FROM books
INNER JOIN authors ON books.author_id = authors.id;

-- LEFT JOIN: all books, NULLs where no author is linked
SELECT books.title, authors.name AS author
FROM books
LEFT JOIN authors ON books.author_id = authors.id;

-- Find books with no author assigned
SELECT books.title
FROM books
LEFT JOIN authors ON books.author_id = authors.id
WHERE authors.id IS NULL;""",
        "hints": [
            "SQLite allows adding columns with ALTER TABLE ADD COLUMN.",
            "After ALTER TABLE, run .schema books to see the new column.",
            "In a JOIN query, prefix ambiguous column names: books.id, authors.id.",
            "LEFT JOIN keeps all rows from the left (first) table.",
        ],
        "reflection": [
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "What happens if author_id in books does not match any id in authors?",
            "Could you store author name directly in books? What are the downsides?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
        ],
    },
    {
        "id": 12,
        "title": "Indexes",
        "concept": "CREATE INDEX, EXPLAIN QUERY PLAN",
        "intro": """\
Exercise 12 — Indexes

An index is a separate data structure that lets the database find rows without
scanning every row in the table.  Think of it like the index at the back of a
book: you pay a small cost to maintain it, and in return you get much faster
lookups.

When to add an index:
  ✔  Columns you frequently use in WHERE clauses
  ✔  Columns you JOIN on (foreign keys)
  ✔  Columns you frequently ORDER BY

When NOT to add an index:
  ✗  Very small tables (full scan is fine)
  ✗  Columns you rarely query
  ✗  Tables with very frequent INSERTs/UPDATEs (write overhead)

Syntax:
  CREATE INDEX idx_name ON table_name(column);""",
        "tasks": [
            "Create an index on books.genre.",
            "Create an index on books.author_id.",
            "Use EXPLAIN QUERY PLAN to see how a query uses the index.",
            "Use .schema books to confirm the indexes exist.",
            "DROP one index and re-run EXPLAIN QUERY PLAN to compare.",
        ],
        "example_sql": """\
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_books_genre    ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_author   ON books(author_id);

-- See query plan WITH the index
EXPLAIN QUERY PLAN SELECT * FROM books WHERE genre = 'Fiction';

-- See all indexes
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index';

-- Drop an index
DROP INDEX idx_books_genre;

-- See query plan WITHOUT the index
EXPLAIN QUERY PLAN SELECT * FROM books WHERE genre = 'Fiction';""",
        "hints": [
            "EXPLAIN QUERY PLAN does not run the query — it shows the plan only.",
            "Look for 'USING INDEX' in the plan output to confirm the index is used.",
            "SQLite automatically creates an index for PRIMARY KEY and UNIQUE columns.",
            "IF NOT EXISTS prevents an error if the index already exists.",
        ],
        "reflection": [
            "What does 'SCAN TABLE books' in the query plan mean?",
            "What does 'SEARCH TABLE books USING INDEX' mean?",
            "If you have 1 million books, how does an index change query speed?",
            "What is the cost of having too many indexes?",
        ],
        "setup": [
            """CREATE TABLE IF NOT EXISTS authors (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  birth_year INTEGER
);""",
            """CREATE TABLE IF NOT EXISTS books (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  title          TEXT NOT NULL,
  genre          TEXT,
  year_published INTEGER
);""",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (1, 'Toni Morrison', 1931);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (2, 'George Orwell', 1903);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (3, 'James Baldwin', 1924);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (4, 'Octavia Butler', 1947);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (5, 'Ursula K. Le Guin', 1929);",
            "INSERT OR IGNORE INTO authors (id, name, birth_year) VALUES (6, 'Zora Neale Hurston', 1891);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (1, 'Beloved', 'Fiction', 1987);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (2, 'Nineteen Eighty-Four', 'Fiction', 1949);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (3, 'Go Tell It on the Mountain', 'Fiction', 1953);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (4, 'Kindred', 'Science Fiction', 1979);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (5, 'The Left Hand of Darkness', 'Science Fiction', 1969);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (6, 'Their Eyes Were Watching God', 'Fiction', 1937);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (7, 'Animal Farm', 'Satire', 1945);",
            "INSERT OR IGNORE INTO books (id, title, genre, year_published) VALUES (8, 'Parable of the Sower', 'Science Fiction', 1993);",
            "ALTER TABLE books ADD COLUMN author_id INTEGER;",
            "UPDATE books SET author_id = 1 WHERE title = 'Beloved';",
            "UPDATE books SET author_id = 2 WHERE title LIKE '%Eighty%';",
            "UPDATE books SET author_id = 3 WHERE title LIKE '%Mountain%';",
            "UPDATE books SET author_id = 4 WHERE title = 'Kindred';",
            "UPDATE books SET author_id = 4 WHERE title LIKE '%Sower%';",
            "UPDATE books SET author_id = 5 WHERE title LIKE '%Darkness%';",
            "UPDATE books SET author_id = 6 WHERE title LIKE '%Watching%';",
            "UPDATE books SET author_id = 2 WHERE title = 'Animal Farm';",
        ],
    },
]

# ── Exercise runner ───────────────────────────────────────────────────────────

def run_setup(conn, exercise):
    """Run the setup SQL for an exercise silently."""
    for stmt in exercise.get("setup", []):
        try:
            conn.execute(stmt)
            conn.commit()
        except sqlite3.OperationalError as e:
            # Silently ignore "duplicate column" errors from ALTER TABLE
            msg = str(e).lower()
            if "duplicate column" in msg or "already exists" in msg:
                pass
            else:
                print(c(f"  [setup warning] {e}", DIM))
        except sqlite3.Error as e:
            print(c(f"  [setup warning] {e}", DIM))


def run_exercise(exercise, progress):
    conn = get_connection()
    run_setup(conn, exercise)

    banner(f"Exercise {exercise['id']} — {exercise['title']}")

    section("Concept")
    info(exercise["concept"])

    section("Introduction")
    for line in textwrap.dedent(exercise["intro"]).splitlines():
        info(line)

    if exercise.get("example_sql"):
        section("Example SQL")
        for line in exercise["example_sql"].splitlines():
            print(c(f"  {line}", CYAN))

    section("Your Tasks")
    for i, task in enumerate(exercise["tasks"], 1):
        print(c(f"  {i}. {task}", WHITE))

    print(c("""
  ─────────────────────────────────────────────────────────────────────
  Type SQL statements or dot-commands and press Enter to run them.
  Special commands:
    .hints   — show hints for this exercise
    .tasks   — show the task list again
    .example — show the example SQL again
    .reflect — show reflection questions
    .done    — mark this exercise complete and return to menu
    .menu    — return to the main menu without marking done
    .reset   — drop library.db and start fresh (CAUTION!)
    .help    — dot-command reference
  ─────────────────────────────────────────────────────────────────────
""", DIM))

    while True:
        try:
            user_input = prompt_line()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user_input:
            continue

        low = user_input.lower()

        if low == ".done":
            mark_done(exercise["id"], progress)
            success(f"Exercise {exercise['id']} marked complete!  Great work.")
            print()
            conn.close()
            return "menu"

        if low == ".menu":
            conn.close()
            return "menu"

        if low == ".reset":
            confirm = input(c(
                "  Are you sure you want to delete library.db? (yes/no): ", YELLOW
            )).strip().lower()
            if confirm == "yes":
                conn.close()
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                success("library.db deleted.  Restart the tutor to begin fresh.")
                sys.exit(0)
            else:
                print(c("  Reset cancelled.", DIM))

        elif low == ".hints":
            section("Hints")
            for h in exercise.get("hints", []):
                hint_text(h)

        elif low == ".tasks":
            section("Tasks")
            for i, task in enumerate(exercise["tasks"], 1):
                print(c(f"  {i}. {task}", WHITE))

        elif low == ".example":
            if exercise.get("example_sql"):
                section("Example SQL")
                for line in exercise["example_sql"].splitlines():
                    print(c(f"  {line}", CYAN))
            else:
                print(c("  No example SQL for this exercise.", DIM))

        elif low == ".reflect":
            section("Reflection Questions")
            for q in exercise.get("reflection", []):
                print(c(f"  ?  {q}", MAGENTA))

        elif user_input.startswith("."):
            handle_dot_command(conn, user_input)

        else:
            run_sql(conn, user_input)


# ── Main menu ────────────────────────────────────────────────────────────────

def print_menu(progress):
    banner("SQLite3 Library — Interactive SQL Tutor")
    print(c("""
  This tutor walks you through SQL fundamentals using a small public-
  library database (library.db).  Each exercise builds on the last.

  Commands at the menu prompt:
    <number>   — go to that exercise (e.g. type  3  for Exercise 3)
    c          — go to the Capstone Challenge
    r          — reset all progress (does NOT delete library.db)
    q          — quit
""", WHITE))

    print(c("  EXERCISES", BOLD + YELLOW))
    print(c("  " + "─" * 50, DIM))
    for ex in EXERCISES:
        done = ex["id"] in progress["completed"]
        marker = c("✔", GREEN + BOLD) if done else c("○", DIM)
        num_str = c(f"{ex['id']:>2}.", BOLD)
        title   = c(ex["title"], WHITE if not done else DIM)
        concept = c(f"  [{ex['concept']}]", DIM)
        print(f"  {marker} {num_str} {title}{concept}")

    cap_done = "capstone" in progress["completed"]
    cap_marker = c("✔", GREEN + BOLD) if cap_done else c("○", DIM)
    print(c("  " + "─" * 50, DIM))
    print(f"  {cap_marker}  {c('C.', BOLD)} {c('Capstone Challenge', WHITE if not cap_done else DIM)}")
    print()


def run_capstone(progress, conn=None):
    if conn is None:
        conn = get_connection()

    seed_path = os.path.join(os.path.dirname(__file__), "capstone", "seed.sql")
    questions_path = os.path.join(os.path.dirname(__file__), "capstone", "questions.md")

    banner("Capstone Mini-Challenge — Music Catalog")
    info("""\
In this challenge you work with a brand-new music catalog database.
The data has already been loaded into your library.db under the tables:
  artists, albums, tracks, genres

Your job: answer 10 questions using only SQL queries.
Write your final queries to a file called  capstone_answers.sql  and
save it alongside this tutor.
""")

    # Load seed data
    if os.path.exists(seed_path):
        print(c("  Loading music catalog seed data …", DIM))
        with open(seed_path) as f:
            seed_sql = f.read()
        statements = [s.strip() for s in seed_sql.split(";") if s.strip()]
        for stmt in statements:
            try:
                conn.execute(stmt)
                conn.commit()
            except sqlite3.Error as e:
                msg = str(e).lower()
                if "already exists" in msg or "duplicate" in msg:
                    pass
                else:
                    print(c(f"  [seed warning] {e}", DIM))
        success("Seed data loaded.")
    else:
        error("capstone/seed.sql not found.  Make sure you haven't moved any files.")
        return "menu"

    # Show questions
    if os.path.exists(questions_path):
        section("Your Questions")
        with open(questions_path) as f:
            for line in f:
                info(line.rstrip())
    else:
        error("capstone/questions.md not found.")

    print(c("""
  ─────────────────────────────────────────────────────────────────────
  Use .tables and .schema to explore the music catalog tables.
  Type SQL to answer each question.
  Type .done when you have finished the capstone.
  ─────────────────────────────────────────────────────────────────────
""", DIM))

    while True:
        try:
            user_input = prompt_line()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user_input:
            continue

        low = user_input.lower()

        if low == ".done":
            mark_done("capstone", progress)
            success("Capstone complete!  Well done — you've finished the course.")
            print()
            conn.close()
            return "menu"

        if low == ".menu":
            conn.close()
            return "menu"

        elif user_input.startswith("."):
            handle_dot_command(conn, user_input)
        else:
            run_sql(conn, user_input)

    conn.close()
    return "menu"


def main():
    progress = load_progress()

    while True:
        print_menu(progress)
        try:
            choice = input(c("  Enter choice: ", BOLD + GREEN)).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(c("\n  Goodbye!\n", BOLD + CYAN))
            sys.exit(0)

        if choice == "q":
            print(c("\n  Goodbye!  Keep practicing.\n", BOLD + CYAN))
            sys.exit(0)

        if choice == "r":
            confirm = input(c(
                "  Reset all progress? This will NOT delete library.db. (yes/no): ", YELLOW
            )).strip().lower()
            if confirm == "yes":
                progress = {"completed": []}
                save_progress(progress)
                success("Progress reset.")
            continue

        if choice == "c":
            run_capstone(progress)
            continue

        try:
            ex_num = int(choice)
        except ValueError:
            print(c("  Please enter a number (1–12), 'c' for Capstone, or 'q' to quit.", YELLOW))
            continue

        matched = [e for e in EXERCISES if e["id"] == ex_num]
        if not matched:
            print(c(f"  No exercise #{ex_num}. Choose 1–{len(EXERCISES)}.", YELLOW))
            continue

        result = run_exercise(matched[0], progress)
        if result == "menu":
            continue


if __name__ == "__main__":
    main()
