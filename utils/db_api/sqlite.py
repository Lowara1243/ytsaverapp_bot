import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path_to_db=Path(Path(r'data\users_settings.sqlite3'))):
        self.path_to_db = path_to_db  # if test.py doesn't work, try this path:
        # Path(r'C:\Users\Olyx\Desktop\python\projects\tbot\data\users_settings.sqlite3')

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection

        cursor = connection.cursor()
        connection.set_trace_callback(logger)
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchone()

        connection.close()

        return data

    def create_table_users(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users (
        id int NOT NULL,
        name text NOT NULL,
        pVidQuality str,
        pAudioQuality str,
        segmentsToMark list,
        segmentsToDelete list,
        PRIMARY KEY (id)
        );
        '''
        self.execute(sql, commit=True)

    def add_user(self, id: int, name: str,
                 pVidQuality: str, pAudioQuality: str,
                 segmentsToMark: list, segmentsToDelete: list):
        sql = '''
        INSERT INTO users (id, name, pVidQuality, pAudioQuality, segmentsToMark, segmentsToDelete)
        VALUES (?, ?, ?, ?, ?, ?);
        '''
        parameters = id, name, pVidQuality, pAudioQuality, segmentsToMark, segmentsToDelete
        self.execute(sql, parameters=parameters, commit=True)

    def select_all_users(self):
        sql = '''
        SELECT * FROM users;
        '''
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' AND '.join([
            f'{item} = ?' for item in parameters
        ])
        return sql, tuple(parameters.values())

    def select_user(self, **kwargs):

        sql = 'SELECT * FROM users WHERE '
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def delete_user(self, **kwargs):

        sql = 'DELETE FROM users WHERE '
        sql, parameters = self.format_args(sql, kwargs)
        print(f'{sql=}\n{parameters=}')
        self.execute(sql, parameters, fetchone=True, commit=True)

    def count_users(self):
        return self.execute('SELECT COUNT(*) FROM users;', fetchone=True)

    def change_params(self, **kwargs):
        list_of_items = [item for item in kwargs]
        sql = f'UPDATE users SET {list_of_items[0]} = ? WHERE '
        sql += ' AND '.join([
            f'{item} = ?' for item in list_of_items[1::]
        ])
        parameters = tuple(kwargs.values())
        return self.execute(sql, parameters, fetchone=True, commit=True)


def logger(statement):
    print(f'''
____________________________________________________
Executing:
{statement}
____________________________________________________
''')
