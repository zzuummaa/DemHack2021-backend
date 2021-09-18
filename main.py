from flask import Flask, jsonify, request

import vk_integration
from database import *
from vk_integration import *
from timer_api import *

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


@app.errorhandler(vk_api.VkApiError)
def handle_rest_api_error(e):
    if isinstance(e, vk_api.ApiError):
        return my_response(error="VK API: " + e.error["error_msg"], code=502)
    return my_response(error="VK API: " + str(e), code=500)


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
    token = get_db().get_vk_api(user_id)
    if token is None:
        return my_response(error="Need VK auth", code=404)

    posts = wall_to_posts(get_wall(token))
    return my_response({"posts": posts})


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

    local_id = action["local_id"]
    action_type = action["type"]

    action_name = get_db().get_action_name_by_type(action_type)
    if action_name is None:
        raise RestApiError(message=f"Unknown action type: {action_type}", code=400)
    elif action_name == 'action_vk_delete_posts':
        if "post_ids" not in action:
            print(action)
            raise RestApiError(message="Invalid request parameters: need post_ids field to use action_vk_delete_posts", code=400)
        get_db().add_action_vk_delete_post(group_id, local_id, action["post_ids"])
    elif action_name == 'action_vk_delete_dialogs':
        if "dialog_ids" not in action:
            raise RestApiError(message="Invalid request parameters: need dialog_ids field to use action_vk_delete_dialogs",
                               code=400)
        get_db().action_vk_delete_dialogs(group_id, local_id, action["dialog_ids"])
    else:
        print('Not realized yet')


def add_trigger_internal(group_id, trigger):
    if "local_id" not in trigger or "type" not in trigger:
        raise RestApiError(message="Invalid request parameters", code=400)

    local_id = trigger["local_id"]
    trigger_type = trigger["type"]

    trigger_name = get_db().get_trigger_name_by_type(trigger_type)
    if trigger_name is None:
        raise RestApiError(message=f"Unknown trigger type: {trigger_type}", code=400)
    elif trigger_name == 'trigger_canary':
        if "link" not in trigger:
            raise RestApiError(message="Invalid request parameters: need link field to use trigger_canary",
                               code=400)
        get_db().add_trigger_canary(group_id, local_id, trigger["link"])
    elif trigger_name == 'trigger_timer':
        if "left_time" not in trigger:
            raise RestApiError(message="Invalid request parameters: need left_time field to use trigger_timer",
                               code=400)
        get_db().add_trigger_timer(group_id, local_id, trigger["left_time"])
    elif trigger_name == 'trigger_sms':
        if "key_word" not in trigger:
            raise RestApiError(message="Invalid request parameters: need key_word field to use trigger_sms",
                               code=400)
        get_db().add_trigger_sms(group_id, local_id, trigger["key_word"])
    else:
        print('Not realized yet')


def get_static_groups():
    return {
        "groups": [
            {
                "group_id": 1,
                "name": "Группа 1",
                "triggers": [
                    {
                        "local_id": 0,
                        "type": 0,
                        "link": "https://example.com/"
                    },
                    {
                        "local_id": 1,
                        "type": 1,
                        "left_time": "48900"
                    }
                ],
                "actions": [
                    {
                        "local_id": 0,
                        "type": 0,
                        "post_ids": [123, 124]
                    }
                ]
            },
            {
                "group_id": 2,
                "name": "Группа 2 (Особенная!)",
                "triggers": [
                    {
                        "local_id": 0,
                        "type": 2,
                        "key_word": "my_super_secret_sms"
                    },
                    {
                        "local_id": 1,
                        "type": 0,
                        "link": "https://example.com"
                    }
                ],
                "actions": [
                    {
                        "local_id": 0,
                        "type": 0,
                        "post_ids": [123, 124]
                    }
                ]
            }
        ]
    }


@app.route('/groups', methods=['GET'])
def get_groups():
    if "user_id" not in request.args:
        raise RestApiError(message="Invalid request parameters", code=400)

    return my_response(get_static_groups())


@app.route('/groups', methods=['POST'])
def add_group():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "user_id" not in request.json \
            or "name" not in request.json \
            or "actions" not in request.json \
            or "triggers" not in request.json:
        return my_response(error="Invalid request parameters", code=400)

    user_id = request.json["user_id"]
    group_name = request.json["name"]

    group_id = get_db().create_new_group(group_name, user_id)

    for action in request.json["actions"]:
        add_action_internal(group_id, action)

    for trigger in request.json["triggers"]:
        add_trigger_internal(group_id, trigger)

    return my_response({"group_id": group_id})


@app.route('/groups', methods=['DELETE'])
def delete_group():
    if "group_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    # TODO db: remove_trigger()

    return my_response()


@app.route('/actions', methods=['POST'])
def add_action():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    action_id = add_action_internal(group_id, request.json)

    return my_response({"action_id": action_id})


@app.route('/actions', methods=['PUT'])
def update_action():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args or "local_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    local_id = request.args["local_id"]

    # TODO update fields, such is present in json

    return my_response()


@app.route('/actions', methods=['DELETE'])
def delete_action():
    if "action_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    action_id = request.args["action_id"]
    # TODO db: remove_action()

    return my_response()


@app.route('/triggers', methods=['POST'])
def add_trigger():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    action_id = add_trigger_internal(group_id, request.json)

    return my_response({"trigger_id": action_id})


@app.route('/triggers', methods=['PUT'])
def update_trigger():
    if not request.is_json:
        return my_response(error="Body should contains JSON", code=400)

    if "group_id" not in request.args or "local_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    group_id = request.args["group_id"]
    local_id = request.args["local_id"]

    # TODO update fields, such is present in json

    return my_response()


@app.route('/triggers', methods=['DELETE'])
def delete_trigger():
    if "trigger_id" not in request.args:
        return my_response(error="Invalid request parameters", code=400)

    trigger_id = request.args["trigger_id"]
    # TODO db: remove_trigger()

    return my_response()


if __name__ == '__main__':
    timer_loop.start()

    conn = connect()
    cursor = conn.cursor()
    create_tables(cursor)
    conn.commit()
    conn.close()

    app.run(debug=True, host='0.0.0.0', port=80)
