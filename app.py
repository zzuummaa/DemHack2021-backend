from flask import Flask, jsonify, request, g
from database import *

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = DatabaseWrapper(connect())
    return db


@app.route('/')
def index():
    rows = get_db().query_db("""SELECT hello_string FROM test LIMIT 1""")
    return {"message": str(rows[0][0])}


if __name__ == '__main__':
    conn = connect()
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()

    app.run(debug=True, host='0.0.0.0', port=80)
