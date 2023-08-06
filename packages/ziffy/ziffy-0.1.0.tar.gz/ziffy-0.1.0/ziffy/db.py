import sqlite3

def init_db(con):
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS datasets(
                dataset VARCHAR UNIQUE,
                id INTEGER PRIMARY KEY,
                cr_txg INTEGER,
                size INTEGER,
                objects INTEGER
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS tree(
                dataset VARCHAR,
                id INTEGER PRIMARY KEY,
                path VARCHAR UNIQUE,
                target VARCHAR NULL,
                uid INTEGER,
                gid INTEGER,
                atime VARCHAR,
                mtime VARCHAR,
                ctime VARCHAR,
                crtime VARCHAR,
                gen INTEGER,
                mode VARCHAR,
                size INTEGER,
                parent INTEGER
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS file_path ON tree(path)")
        con.commit()
