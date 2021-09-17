import psycopg2


class DatabaseWrapper:
    def __init__(self, db):
        self.database = db

    def query_db(self, query, args=(), ret_lastrowid=False, ret_rowcount=False):
        cur = self.database.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        self.database.commit()
        if ret_lastrowid:
            return cur.lastrowid
        elif ret_rowcount:
            return cur.rowcount
        return rv

    def execute(self, *args):
        return self.database.execute(args)

    def close(self):
        self.database.close()


def connect():
    db = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="mysecretpassword",
        host="45.134.255.158",
        port="5432"
    )
    return db


def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test (
            hello_string varchar(256) PRIMARY KEY
        )
    """)
    cursor.execute("""
        INSERT INTO test (hello_string) VALUES ('Hello, Postgress 2!')
        ON CONFLICT (hello_string) DO NOTHING;
    """)

