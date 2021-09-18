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

    def insert_db(self, query, args=()):
        cur = self.database.cursor()
        cur.execute(query, args)
        self.database.commit()

    def execute(self, *args):
        return self.database.execute(args)

    def close(self):
        self.database.close()

    def create_new_user(self, new_name):
        new_id = self.query_db("select coalesce(max(id),0) from users;")[0][0] + 1
        self.insert_db(
            """
            insert into users (id, name)
            VALUES (%s, %s);
            """, (new_id, new_name))
        return new_id


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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            name VARCHAR(128));
        """)
