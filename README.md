# DatabasesSQLite3 — Interactive SQL Tutor

A terminal-based project that walks adult students through SQL fundamentals
using SQLite3.  No prior SQL experience required.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.8 +   |
| sqlite3     | bundled with Python |

Check your Python version:
```bash
python3 --version
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ZipCodeCore/DatabasesSQLite3.git
cd DatabasesSQLite3

# Launch the tutor
python3 tutor.py
```

The tutor creates `library.db` in the project directory on first use.
No installation or setup beyond Python 3 is needed.

---

## How It Works

The tutor presents **12 progressive exercises** followed by a **Capstone
Challenge**, all using a single consistent dataset — a small public-library
database (`library.db`).

At the main menu, type a number to enter an exercise.  Inside each exercise
you get:

- A plain-English explanation of the concept
- Example SQL you can copy, paste, and modify
- A task list to complete
- On-demand hints (`.hints`)
- Reflection questions (`.reflect`)
- A mark-complete command (`.done`)

### Exercise Overview

| # | Title | Concept |
|---|-------|---------|
| 1 | What is a Database? | Relational model, dot-commands |
| 2 | Creating Tables | `CREATE TABLE`, data types |
| 3 | Inserting Data | `INSERT INTO … VALUES` |
| 4 | Querying Data | `SELECT`, `FROM`, `WHERE` |
| 5 | Filtering and Sorting | `WHERE` operators, `ORDER BY`, `LIMIT` |
| 6 | Updating Records | `UPDATE … SET … WHERE` |
| 7 | Deleting Records | `DELETE FROM … WHERE` |
| 8 | Primary Keys and Uniqueness | `PRIMARY KEY`, `UNIQUE` |
| 9 | Aggregate Functions | `COUNT`, `AVG`, `MIN`, `MAX` |
| 10 | Grouping Data | `GROUP BY`, `HAVING` |
| 11 | Joins | `INNER JOIN`, `LEFT JOIN`, foreign keys |
| 12 | Indexes | `CREATE INDEX`, `EXPLAIN QUERY PLAN` |
| C | Capstone Challenge | Music catalog — 10 open-ended questions |

---

## Project Layout

```
DatabasesSQLite3/
├── tutor.py                 # Main interactive tutor
├── library.db               # Created at runtime (not committed)
├── capstone/
│   ├── seed.sql             # Music catalog seed data
│   ├── questions.md         # 10 capstone questions + bonus
│   └── capstone_answers.sql # Answer template (fill this in)
└── README.md
```

---

## Tutor Commands

These commands work inside any exercise:

| Command    | Description |
|------------|-------------|
| `.hints`   | Show hints for the current exercise |
| `.tasks`   | Show the task list again |
| `.example` | Show example SQL again |
| `.reflect` | Show reflection questions |
| `.done`    | Mark exercise complete, return to menu |
| `.menu`    | Return to menu without marking done |
| `.tables`  | List all tables in the database |
| `.schema [table]` | Show CREATE statement |
| `.databases` | Show attached database file |
| `.read <file>` | Execute SQL from a file |
| `.reset`   | Delete `library.db` and start fresh |
| `.help`    | Show all dot-commands |
| `.quit`    | Exit the tutor |

---

## Capstone Challenge

After completing the 12 exercises, select **C** from the main menu.  The
tutor loads a music catalog database (artists, albums, tracks, genres) and
presents 10 SQL questions.

Write your final queries in `capstone/capstone_answers.sql`.

---

## Progress

Progress is saved to `.progress.json` in the project directory.  To reset
your progress without deleting the database, choose **r** from the main menu.
To wipe the database entirely, type `.reset` inside any exercise.

---

## Learning Path

```
Exercise 1  →  What databases are and why they matter
     ↓
Exercise 2–3  →  Create tables and insert data (DDL + DML)
     ↓
Exercise 4–5  →  Query and filter data (SELECT, WHERE, ORDER BY)
     ↓
Exercise 6–7  →  Modify and remove data (UPDATE, DELETE)
     ↓
Exercise 8    →  Constraints (PRIMARY KEY, UNIQUE)
     ↓
Exercise 9–10 →  Summarize data (aggregates, GROUP BY)
     ↓
Exercise 11   →  Relate tables (JOINs, foreign keys)
     ↓
Exercise 12   →  Performance (indexes, EXPLAIN QUERY PLAN)
     ↓
Capstone      →  Apply everything on a fresh dataset
```