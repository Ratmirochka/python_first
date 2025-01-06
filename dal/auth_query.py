from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

class DbQuery():
    @staticmethod
    def get_passw(login):
        cursor = DbConnection.connect_to_db()
        if cursor:
            try:
                cursor.execute('SELECT password FROM Users WHERE login = %s', (login,))
                return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при входе : {e}")
        else:
            return None

    @staticmethod
    def get_user(login):
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                            select u.user_id, u.name AS name, u.post, r.name AS role
                            from users u
                            inner join role r using (role_id)
                            where login = %s
                            """, (login,))
                    return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при получении полей пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"