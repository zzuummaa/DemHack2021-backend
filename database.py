import psycopg2
import uuid
from flask import g

import utils


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

    def insert_or_update_db(self, query, args=()):
        cur = self.database.cursor()
        cur.execute(query, args)
        self.database.commit()

    def execute(self, *args):
        return self.database.execute(args)

    def close(self):
        self.database.close()

    def create_new_user(self, new_name):
        new_id = uuid.uuid4().hex
        # new_id = self.query_db("select coalesce(max(id),0) from users;")[0][0] + 1
        self.insert_or_update_db(
            """
            insert into users (id, name)
            VALUES (%s, %s);
            """,
            (new_id, new_name))
        return new_id

    def create_new_group(self, group_name, user_id):
        new_group_id = self.query_db("select coalesce(max(id),0) from groups;")[0][0] + 1
        self.insert_or_update_db(
            """
            insert into groups (id, name, user_id)
            VALUES (%s, %s, %s);
            """,
            (new_group_id, group_name, user_id))
        return new_group_id

    def get_vk_token_by_group(self, group_id):
        query_result = self.query_db(
            """
            SELECT user_id FROM groups WHERE id = %s;
            """,
            args=(group_id,))

        if len(query_result) and len(query_result[0]):
            return query_result[0][0]


    def get_groups_by_user(self, user_id):
        query_result = self.query_db(
            """
            SELECT id, name FROM groups WHERE user_id = %s;
            """,
            args=(user_id,))

        groups_ids_with_name = []

        for group_id, group_name in query_result:
            groups_ids_with_name.append((group_id, group_name))

        return groups_ids_with_name

    def get_user_by_group(self, group_id):
        query_result = self.query_db(
            """
            SELECT user_id FROM groups WHERE id = %s;
            """,
            args=(group_id,))

        if len(query_result) and len(query_result[0]):
            return query_result[0][0]

    def add_vk_api(self, user_id, vk_api):
        self.insert_or_update_db(
            """
            UPDATE users SET vk_api = %s WHERE id = %s;
            """,
            (vk_api, user_id))

    def get_vk_api(self, user_id):
        query_result = self.query_db(
            """
            SELECT vk_api FROM users WHERE id = %s;
            """,
            args=(user_id,))

        if len(query_result) and len(query_result[0]):
            return query_result[0][0]

    def get_action_name_by_type(self, action_type):
        query_result = self.query_db(
            """
            SELECT table_name FROM actions WHERE type = %s;
            """,
            args=(action_type,))

        if len(query_result) and len(query_result[0]):
            return query_result[0][0]

    def get_trigger_name_by_type(self, trigger_type):
        query_result = self.query_db(
            """
            SELECT table_name FROM triggers WHERE type = %s;
            """,
            args=(trigger_type,))

        if len(query_result) and len(query_result[0]):
            return query_result[0][0]

    def get_all_post_ids_from_action_vk_delete_dialogs(self, group_id):
        all_actions_in_db = self.query_db(
            """
            SELECT * FROM action_vk_delete_dialogs WHERE group_id = %s;
            """,
            (group_id,))

        dialog_ids = []

        for _, _, row_dialog_ids in all_actions_in_db:
            dialog_ids.append(row_dialog_ids.split(','))

        return dialog_ids


    def get_all_post_ids_from_action_vk_delete_posts(self, group_id):
        all_actions_in_db = self.query_db(
            """
            SELECT * FROM action_vk_delete_posts WHERE group_id = %s;
            """,
            (group_id,))

        post_ids = []

        for _, _, row_post_ids in all_actions_in_db:
            post_ids.append(row_post_ids.split(','))

        return post_ids


    def clear_group_after_trigger(self, group_id):
        self.insert_or_update_db(
            """
            DELETE FROM groups CASCADE where id = %s;
            """,
            (group_id,))


    def get_action_vk_delete_dialogs(self, group_id):
        all_actions_in_db = self.query_db(
            """
            SELECT local_id, dialog_ids FROM action_vk_delete_dialogs WHERE group_id = %s;
            """,
            (group_id,))

        res = []
        for local_id, dialog_ids_str in all_actions_in_db:
            res.append((local_id, dialog_ids_str.split(',')))
        return res


    def get_trigger_sms(self, group_id):
        all_trigger_sms_in_db = self.query_db(
            """
            SELECT local_id, key_word FROM trigger_sms WHERE group_id = %s;
            """,
            (group_id,))

        res = []
        for local_id, key_word in all_trigger_sms_in_db:
            res.append((local_id, key_word))

        return res


    def get_trigger_canary(self, group_id):
        all_canary_in_db = self.query_db(
            """
            SELECT local_id, link FROM trigger_canary WHERE group_id = %s;
            """,
            (group_id,))

        res = []
        for local_id, link in all_canary_in_db:
            res.append((local_id, link))

        return res

    def get_trigger_timer(self, group_id):
        all_timers_in_db = self.query_db(
            """
            SELECT local_id, expiration_dt FROM trigger_timer WHERE group_id = %s;
            """,
            (group_id,))

        res = []
        for local_id, expiration_dt in all_timers_in_db:
            res.append((local_id, utils.get_seconds_till_timestamp(expiration_dt)))

        return res

    def get_action_vk_delete_posts(self, group_id):
        all_actions_in_db = self.query_db(
            """
            SELECT local_id, post_ids FROM action_vk_delete_posts WHERE group_id = %s;
            """,
            (group_id,))

        res = []
        for local_id, post_ids_str in all_actions_in_db:
            res.append((local_id, post_ids_str.split(',')))

        return res


    def action_vk_delete_dialogs(self, group_id, local_id, dialog_ids):
        # Serrialize posts_ids array to string
        dialog_ids_str = ",".join([str(post_id) for post_id in dialog_ids])

        self.insert_or_update_db(
            """
            insert into action_vk_delete_dialogs (group_id, local_id, dialog_ids)
            VALUES (%s, %s, %s);
            """,
            (group_id, local_id, dialog_ids_str))

    def add_action_vk_delete_post(self, group_id, local_id, post_ids):
        # Serrialize posts_ids array to string
        post_ids_str = ",".join([str(post_id) for post_id in post_ids])

        self.insert_or_update_db(
            """
            insert into action_vk_delete_posts (group_id, local_id, post_ids)
            VALUES (%s, %s, %s);
            """,
            (group_id, local_id, post_ids_str))


    def add_trigger_canary(self, group_id, local_id, link):
        self.insert_or_update_db(
            """
            insert into trigger_canary (group_id, local_id, link)
            VALUES (%s, %s, %s);
            """,
            (group_id, local_id, link))


    def add_trigger_sms(self, group_id, local_id, key_word):
        self.insert_or_update_db(
            """
            insert into trigger_sms (group_id, local_id, key_word)
            VALUES (%s, %s, %s);
            """,
            (group_id, local_id, key_word))


    def add_trigger_timer(self, group_id, local_id, left_time_seconds):
        #TODO: Convert to str post_ids

        self.insert_or_update_db(
            """
            insert into trigger_timer (group_id, local_id, expiration_dt)
            VALUES (%s, %s, %s);
            """,
            (group_id, local_id, utils.get_timestamp_after_seconds(int(left_time_seconds))))


    def get_all_timers(self):
        all_timers_rows_in_db = self.query_db(
            """
            SELECT group_id, expiration_dt FROM trigger_timer;
            """)

        return all_timers_rows_in_db


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = DatabaseWrapper(connect())
    return db


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
            id VARCHAR(128) PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            vk_api VARCHAR(128));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY,
            name VARCHAR(128) NOT NULL,
            user_id VARCHAR(128) REFERENCES users);
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS triggers (
            type INTEGER PRIMARY KEY,
            table_name VARCHAR(128) NOT NULL);
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trigger_canary(
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            link VARCHAR(128) NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trigger_timer(
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            expiration_dt TIMESTAMP NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trigger_sms(
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            key_word VARCHAR(64) NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS actions (
            type INTEGER PRIMARY KEY,
            table_name VARCHAR(128) NOT NULL);
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_vk_delete_post (
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            post_ids VARCHAR(1024) NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_vk_delete_posts (
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            post_ids VARCHAR(1024) NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_vk_delete_dialogs (
            group_id INTEGER NOT NULL REFERENCES groups ON DELETE CASCADE,
            local_id INTEGER NOT NULL,
            dialog_ids VARCHAR(1024) NOT NULL,
            PRIMARY KEY (group_id, local_id));
        """)