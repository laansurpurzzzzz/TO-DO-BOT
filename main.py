import telebot
from telebot import types
import sqlite3

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

token = '5828591548:AAFPRcmZXc1v2hAkbgLs3QXAXN62JTrOj1M'
bot = telebot.TeleBot(token)


def db_table_val(user_id: int, message: str, status: int):
    cursor.execute('INSERT INTO main ( user_id, message, status) VALUES (?, ?, ?)',
                   (user_id, message, status))
    conn.commit()


def gen_buttons(mess_id, stat_data):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if stat_data == '0':
        stat_button = types.InlineKeyboardButton(text=f'Задача открыта ❌', callback_data=f'{f"{mess_id}{stat_data}"}')
    else:
        stat_button = types.InlineKeyboardButton(text=f'Задача закрыта ✅', callback_data=f'{f"{mess_id}{stat_data}"}')
    del_button = types.InlineKeyboardButton(text='Удалить Запись', callback_data=f'{mess_id}')
    keyboard.add(del_button, stat_button)
    return keyboard


def get_all(message):
    cursor.execute(f"SELECT * FROM main WHERE user_id = '{message.from_user.id}'")
    rows = cursor.fetchall()
    for row in rows:
        id = str(row[0])
        mess = str(row[2])
        status = str(row[3])
        bot.send_message(message.from_user.id, mess, reply_markup=gen_buttons(id, status))


def get_one(message, id):
    cursor.execute(f"SELECT * FROM main WHERE user_id = '{message.from_user.id}'")
    rows = cursor.fetchall()
    for row in rows:
        mess_id = str(row[0])
        mess = str(row[2])
        status = str(row[3])
        if mess_id == id:
            bot.send_message(message.from_user.id, mess, reply_markup=gen_buttons(mess_id, status))


@bot.message_handler(commands=['start'])
def start_message(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Показать все', callback_data='show_all')
    kb.add(btn1)
    bot.send_message(message.chat.id, 'Привет! Чтобы создать заметку просто напиши мне сообщение.', reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: callback.data == 'show_all')
def show_all(message):
    get_all(message)


@bot.callback_query_handler(func=lambda callback: callback.data)
def del_notes(callback):
    cursor.execute(f"SELECT id FROM main")
    rows = cursor.fetchall()
    for row in rows:
        id = str(row[0])
        if callback.data == id:
            cursor.execute(f'DELETE FROM main WHERE id={int(id)}')
            conn.commit()
            bot.delete_message(callback.from_user.id, callback.message.message_id)
        if callback.data == id + '0':
            cursor.execute(f'UPDATE main SET  status = 1 WHERE id = {id}')
            conn.commit()
            bot.delete_message(callback.from_user.id, callback.message.message_id)
            get_one(callback, id)
        elif callback.data == id + '1':
            cursor.execute(f'UPDATE main SET  status = 0 WHERE id = {id}')
            conn.commit()
            bot.delete_message(callback.from_user.id, callback.message.message_id)
            get_one(callback, id)


@bot.message_handler(content_types=['text'])
def handler(message):
    db_table_val(user_id=message.from_user.id, message=message.text, status=0)


bot.polling(none_stop=True)
