## coding a database form scratch
https://trialofcode.org/


## Here's the complete skeleton. Every concept listed is something you need to understand before writing that layer.

---

## The Skeleton of a Relational Database

```
┌─────────────────────────────────┐
│         SQL Interface           │  ← What the user types
├─────────────────────────────────┤
│         Query Parser            │  ← Turns SQL string into a plan
├─────────────────────────────────┤
│        Query Executor           │  ← Runs the plan (scan, join, filter)
├─────────────────────────────────┤
│          B+ Tree Index          │  ← Fast lookups
├─────────────────────────────────┤
│         Buffer Pool             │  ← Memory management
├─────────────────────────────────┤
│         Page Manager            │  ← Fixed-size chunks on disk
├─────────────────────────────────┤
│           Disk / File           │  ← Actual storage
└─────────────────────────────────┘
```

You build **bottom to top**. Each layer depends on the one below it.

---

## Layer 1 — Disk & File Storage

**What it does:** physically stores bytes on disk

**What to understand:**
- Why disk is slow compared to RAM (seek time, read time)
- Why you read/write in fixed-size **pages** (4KB or 8KB) instead of byte by byte
- What `fsync` is and why it matters for crash safety
- How a file is just a sequence of bytes and what that means for your DB

**What to read:**
- OSTEP Chapter 36 — I/O Devices
- CMU 15-445 Note 03 — Database Storage

**Core idea to internalize:**
> A database file is divided into fixed-size pages. Every read and write happens one full page at a time — never individual bytes.

---

## Layer 2 — Page Manager

**What it does:** manages how rows are stored inside pages

**What to understand:**
- Page layout — how a fixed 4KB chunk is organized internally
- Slotted page design — how you store variable-length rows in a fixed-size page
- Page header — stores metadata like how many rows, free space, etc.
- How pages are numbered and how you find page N in a file

**What to read:**
- CMU 15-445 Note 04 — Database Storage II
- Database Internals Ch. 2 — B-Tree Basics (first few pages on page layout)

**Core idea to internalize:**
> A page looks like this internally:
```
┌──────────────────────────────┐
│ Header (metadata)            │
├──────────────────────────────┤
│ Slot 1 → offset 200          │
│ Slot 2 → offset 180          │
│ Slot 3 → offset 150          │
├──────────────────────────────┤
│ Free space                   │
├──────────────────────────────┤
│ Row 3 data       (at 150)    │
│ Row 2 data       (at 180)    │
│ Row 1 data       (at 200)    │
└──────────────────────────────┘
```

---

## Layer 3 — Buffer Pool

**What it does:** keeps frequently used pages in memory so you don't hit disk every time

**What to understand:**
- Why you can't load the entire DB into RAM
- Buffer pool as a cache — a fixed number of frames in memory
- Page replacement policies — LRU (Least Recently Used)
- Dirty pages — a page modified in memory but not yet written to disk
- Pin/unpin — how you tell the buffer pool a page is currently being used

**What to read:**
- CMU 15-445 Note 05 — Buffer Pools
- DDIA Chapter 3 (first half) — Storage and Retrieval

**Core idea to internalize:**
> The buffer pool sits between your code and the disk. Your code never reads the file directly — it always asks the buffer pool for a page, and the buffer pool decides whether to fetch from disk or return a cached copy.

---

## Layer 4 — B+ Tree Index

**What it does:** makes lookups fast — find a row by key in O(log n) instead of scanning everything

**What to understand:**
- Why a sorted array on disk doesn't work well (inserts shift everything)
- Binary tree vs B-Tree vs B+ Tree — why B+ Tree specifically
- B+ Tree structure — internal nodes store keys, leaf nodes store actual data
- How insertion, deletion, and search work
- How leaf nodes are linked as a linked list (enables range queries)
- Tree height — why a B+ Tree with millions of rows is only 3-4 levels deep

**What to read:**
- CMU 15-445 Notes 07-08 — Tree Indexes
- Database Internals Ch. 2-4 — B-Tree deep dive
- Visual tool: **btrees.app** — play with insertions and splits visually before reading

**Core idea to internalize:**
> A B+ Tree with branching factor 100 and 1 million rows is only 3 levels deep. That means any lookup = 3 page reads = 3 disk accesses. That's why indexes are so powerful.

---

## Layer 5 — Query Executor

**What it does:** takes a parsed query and actually executes it using the layers below

**What to understand:**
- Iterator model (Volcano model) — every operator (scan, filter, join) is an iterator with `next()` 
- Sequential scan — reads every page, returns rows one by one
- Index scan — uses B+ Tree to find rows matching a condition
- Filter — takes rows from below, applies WHERE condition
- Join algorithms — Nested Loop Join, Hash Join, Merge Join
- Projection — SELECT only certain columns

**What to read:**
- CMU 15-445 Notes 10-11 — Query Execution
- DDIA Chapter 2 — Data Models and Query Languages

**Core idea to internalize:**
> Every operator is like a pipe. A SELECT with WHERE and JOIN is just operators stacked:
```
Projection (SELECT columns)
    ↑
  Filter (WHERE condition)
    ↑
  Join (combine two tables)
    ↑          ↑
SeqScan A   SeqScan B
```
Each operator pulls rows from below via `next()`.

---

## Layer 6 — SQL Parser

**What it does:** turns a raw SQL string into a structured plan the executor can run

**What to understand:**
- Tokenization — break `SELECT * FROM users WHERE id=1` into tokens
- Parsing — build an Abstract Syntax Tree (AST) from tokens
- Logical plan — what the query means (tree of operations)
- Physical plan — how to actually execute it (which indexes to use etc.)

**What to read:**
- CMU 15-445 Note 12 — Query Planning
- "Crafting Interpreters" Ch. 1-4 (free at craftinginterpreters.com) — best intro to parsing

**Core idea to internalize:**
```
"SELECT id FROM users WHERE age > 20"
          ↓ tokenize
[SELECT] [id] [FROM] [users] [WHERE] [age] [>] [20]
          ↓ parse
AST: Select(columns=[id], table=users, where=GT(age, 20))
          ↓ plan
SeqScan(users) → Filter(age > 20) → Project(id)
```

---

## Layer 7 — Transactions & Recovery

**What it does:** guarantees ACID properties — correctness even with crashes and concurrent users

**What to understand:**
- ACID — Atomicity, Consistency, Isolation, Durability
- Write-Ahead Log (WAL) — log every change before applying it, enables crash recovery
- Transactions — BEGIN, COMMIT, ROLLBACK
- Concurrency control — how multiple transactions don't corrupt each other
- Isolation levels — Read Uncommitted, Read Committed, Repeatable Read, Serializable
- Two-Phase Locking (2PL) — the classic concurrency algorithm

**What to read:**
- DDIA Chapter 7 — Transactions (best written explanation anywhere)
- CMU 15-445 Notes 14-19 — Concurrency and Recovery

**Core idea to internalize:**
> WAL rule: **never write data to disk before writing the log.** If the machine crashes, replay the log to recover. This is how every serious database (PostgreSQL, MySQL, SQLite) survives crashes.

---

## Your Reading & Building Order

| Step | Understand | Then Build |
|---|---|---|
| 1 | Disk, pages, fsync | Write rows to a paged file |
| 2 | Page layout, slotted pages | Page manager with insert/read |
| 3 | Buffer pool, LRU | Buffer pool over your page manager |
| 4 | B+ Tree | B+ Tree index on top of pages |
| 5 | Iterator model, joins | Query executor |
| 6 | Tokenizing, parsing, AST | SQL parser |
| 7 | WAL, ACID, locking | Transactions |

---

## Start Here Right Now

Before writing a single line of code, read these two things in order:

1. **CMU 15-445 Note 03** — Database Storage (free PDF at `15445.courses.cs.cmu.edu/fall2024/notes/03-storage1.pdf`)
2. **CMU 15-445 Note 04** — Database Storage II

These two notes cover Layers 1 and 2 completely. Once you've read them, come back here and we'll start writing Layer 1 together.