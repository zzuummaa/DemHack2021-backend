from flask import Flask, jsonify, request, g
from database import *

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = DatabaseWrapper(connect())
    return db


def my_response(content=None, error=None, code=200):
    if content is None:
        content = {}
    content.update({"error": error, "is_ok": True if code == 200 else False})
    return jsonify(content), code


@app.route('/')
def index():
    rows = get_db().query_db("""SELECT hello_string FROM test LIMIT 1""")
    return {"message": str(rows[0][0]), "test_field": True}


@app.route('/users', methods=['POST'])
def add_user():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "name" not in request.json:
        return my_response(error="Invalid request parameters", code=400)

    name = request.json["name"]

    new_user_id = get_db().create_new_user(name)

    return my_response({'user_id': new_user_id})


@app.route('/vk_api', methods=['POST'])
def add_vk_api():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "user_id" not in request.json or "vk_api_key" not in request.json:
        return my_response(error="Invalid request parameters", code=400)

    user_id = request.json["user_id"]
    vk_api = request.json["vk_api_key"]

    # TODO db

    return my_response()


if __name__ == '__main__':
    conn = connect()
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()

    app.run(debug=True, host='0.0.0.0', port=80)
