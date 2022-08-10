import sqlite3

from utils.db_api.sqlite import Database

db = Database()


def test():
    db.create_table_users()
    users = db.select_all_users()
    print(f'До добавления пользователей: {users=}')
    users = db.select_all_users()
    print(f'После добавления пользователей: {users=}')
    user = db.select_user(id=1491167324)
    print(f'Получил пользователя {user=}')
    db.change_params(name='Olyx', id=1491167324)

test()
