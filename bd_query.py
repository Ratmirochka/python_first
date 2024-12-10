from werkzeug.security import generate_password_hash, check_password_hash
from bd_con import DbConnection

class DbQuery():
    @staticmethod
    def is_corect(login, password):
        cursor = DbConnection.connect_to_db()
        if cursor:
            try:
                cursor.execute('SELECT password FROM Users WHERE login = %s', (login,))
                account = cursor.fetchone()
                if account is None:
                    return False
                return check_password_hash(account[0], password)
            except psycopg2.Error as e:
                print(f"Ошибка при входе : {e}")
        else:
            return None

    @staticmethod
    def insert_new_user(login, password, name, group_id, email):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute('insert into users(login, password, name, group_id, email) values(%s, %s, %s, %s, %s)',
                               (login, generate_password_hash(password), name, group_id, email))
                cursor.connection.commit()
                print(f"Пользователь {name} добавлен")
            except psycopg2.Error as e:
                print(f"Ошибка при добавлении пользователя: {e}")
                return "Не удалось добавить пользователя"
        else:
            return "Не удалось подключиться к базе данных"
