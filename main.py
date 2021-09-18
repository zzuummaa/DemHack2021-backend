from flask import Flask, jsonify, request, g

import vk_integration
from database import *
from vk_integration import *

app = Flask(__name__)


class RestApiError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


@app.errorhandler(RestApiError)
def handle_rest_api_error(e):
    return my_response(error=str(e), code=e.code)


@app.errorhandler(psycopg2.Error)
def handle_rest_api_error(e):
    return my_response(error=str(e.pgerror), code=500)


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

    if not vk_integration.validate_token(vk_api):
        return my_response(error="Invalid token", code=403)

    get_db().add_vk_api(user_id, vk_api)

    return my_response()


@app.route('/vk_api/hook', methods=['GET'])
def vk_api_hook():
    return my_response({"message": "Вернитесь в приложение", "args": request.args})


@app.route('/vk_api/posts', methods=['GET'])
def get_posts():
    if "user_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    user_id = request.args["user_id"]

    # TODO vk_api
    date = get_db().query_db("""select * from test_date""")[0][0]

    return my_response({
        'posts': [
            {'id': 123, 'title': 'Мой пост 1', 'date': '2021-09-18 13:45:19'},
            {'id': 123, 'title': 'Мой пост 2', 'date': '2021-11-10 23:11:00'}
        ]
    })


@app.route('/vk_api/messages', methods=['GET'])
def get_messages():
    if "user_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    user_id = request.args["user_id"]

    return my_response({
        "messages": [
            {
                'id': 123,
                'dialog_name': 'Валерий Клименко'
            },
            {
                'id': 124,
                'dialog_name': 'Степан Фоменко'
            }
        ]
    })


@app.route('/canary/link', methods=['GET'])
def get_canary_link():
    canary_id = uuid.uuid4().hex
    return my_response({
        "canary_id": canary_id,
        "url": "http://45.134.255.15/canary/trigger?canary_id=" + canary_id
    })


@app.route('/canary/trigger', methods=['GET'])
def trigger_canary_link():
    if "canary_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    canary_id = request.args["canary_id"]

    # TODO db: trigger group

    return my_response()


def add_action_internal(group_id, action):
    if "local_id" not in action or "type" not in action:
        raise RestApiError(message="Invalid request parameters", code=400)

    # TODO db: create_action, return action_id

    return 1


def add_triggers_internal(group_id, trigger):
    if "local_id" not in trigger or "type" not in trigger:
        raise RestApiError(message="Invalid request parameters", code=400)

    # TODO db: create_trigger, return trigger_id

    return 1


@app.route('/groups', methods=['POST'])
def add_group():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "user_id" not in request.args \
    or "name" not in request.json \
    or "actions" not in request.json \
    or "triggers" not in request.json:
        return my_response(error="Invalid request parameters", code=400)

    user_id = request.args["user_id"]
    group_name = request.json["name"]

    # TODO db: create_group
    group_id = 1

    for action in request.json["actions"]:
        add_action_internal(group_id, action)

    for trigger in request.json["triggers"]:
        add_action_internal(group_id, trigger)

    return my_response({"group_id": group_id})


@app.route('/actions', methods=['POST'])
def add_action():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    action_id = add_action_internal(group_id, request.json)

    return my_response({"action_id": action_id})


@app.route('/triggers', methods=['POST'])
def add_trigger():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    action_id = add_action_internal(group_id, request.json)

    return my_response({"trigger_id": action_id})


if __name__ == '__main__':
    conn = connect()
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()

    app.run(debug=True, host='0.0.0.0', port=80)
