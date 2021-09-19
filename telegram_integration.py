from threading import Thread

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from actions_processor import process_group_triggered
from database import DatabaseWrapper, connect

bot = telebot.TeleBot('2002969475:AAEN_DJ6RZ1b3n5u2tZ8Zay61ZpGJ8xb5pU', threaded=False)

db = DatabaseWrapper(connect())


@bot.message_handler(commands=['start'])
def start_command(message):
    # bot.send_message(message.chat.id, message)

    nickname = message.from_user.username

    # TODO get_groups_by_telegram_nickname(nickname)
    groups = [{"name": "Vasia", "id": 123}]

    button_list = []
    for group in groups:
        button_list.append([InlineKeyboardButton(group["name"], callback_data=group["id"])])

    reply_markup = InlineKeyboardMarkup(button_list)
    bot.send_message(message.chat.id, "A two-column menu", reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    nickname = call.from_user.username
    # TODO groups = get_groups_by_telegram_nickname(nickname)
    groups = []
    for group in groups:
        process_group_triggered(db, group["id"])


def telegram_start_bot():
    thread = Thread(target=lambda: bot.polling(interval=0, timeout=0, non_stop=True))
    thread.start()


if __name__ == '__main__':
    telegram_start_bot()