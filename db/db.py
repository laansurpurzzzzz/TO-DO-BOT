import sqlite3

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(id: int, user_id: int, message: str, status: int):
    cursor.execute('INSERT INTO main (id, user_id, message, status) VALUES (?, ?, ?, ?)',
                   (id, user_id, message, status))
    conn.commit()
