## File by File
    main.py
    The interactive shell. User types SELECT * FROM users here. It's the entry point that connects all layers together. Like a restaurant's front door.

    disk/disk_manager.py
    The only file that actually touches the database file on disk. Reads and writes raw 4KB pages. Nothing else in the project touches the file directly — everything goes through this.

    storage/page.py
    A page is just raw bytes coming from disk. This file gives those bytes meaning — it knows how rows are packed inside a page, how to insert a row, how to read row 3 out of a page. Turns bytes into actual data.

    buffer/buffer_pool.py
    Disk is slow. This file keeps recently used pages in memory so you don't hit disk every time. When you need a page it checks memory first, only goes to disk if it's not there. Like a cache.

    index/btree.py
    Without this, finding a row means reading every single page. With this, finding a row takes 3-4 page reads regardless of how much data exists. The B+ Tree is the data structure that makes databases fast.

    sql/lexer.py
    Takes a raw SQL string and breaks it into tokens:
    "SELECT id FROM users WHERE age > 20"
    → [SELECT, id, FROM, users, WHERE, age, >, 20]
    Doesn't understand meaning yet — just breaks the string apart.

    sql/parser.py
    Takes those tokens and builds a structured plan:
    [SELECT, id, FROM, users, WHERE, age, >, 20]
    → Query(table=users, columns=[id], condition=age>20)
    Now the database understands what the user wants.

    executor/executor.py
    Takes the parsed query and actually runs it. Calls btree.py to find rows, calls page.py to read them, applies filters, returns results to the user.

    transaction/wal.py
    Write-Ahead Log. Before changing any data, writes what it's about to do to a log file first. If the machine crashes mid-write, this log lets the database recover to a correct state.

    transaction/txn.py
    Manages transactions — BEGIN, COMMIT, ROLLBACK. Makes sure multiple users writing at the same time don't corrupt each other's data.

    data/minidb.db
    The actual database file on disk. Just raw bytes. Everything else in the project exists to read and write this file correctly.

    tests/
    One test file per layer. You write tests here to verify each layer works before building the next one on top of it.

