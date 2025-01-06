from werkzeug.security import generate_password_hash
from psycopg2.extras import RealDictCursor
from db_con import DbConnection
from psycopg2 import Error
from loguru import logger
import psycopg2
import sys
sys.path.append('../')

class DbQuery:
    @staticmethod
    @logger.catch
    def get_passw(login):
        cursor = DbConnection.connect_to_db()
        if cursor:
            try:
                logger.debug(f"Получение пароля для пользователя: {login}")
                cursor.execute('SELECT password FROM Users WHERE login = %s', (login,))
                result = cursor.fetchone()
                if result:
                    logger.debug(f"Пароль найден для пользователя: {login}")
                else:
                    logger.debug(f"Пользователь {login} не найден в базе данных")
                return result
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении пароля для пользователя {login}: {e}")
                return None
        else:
            logger.debug("Не удалось подключиться к базе данных для получения пароля")
            return None

    @staticmethod
    @logger.catch
    def get_user(login):
        con = DbConnection.get_con()
        if con is not None:
            try:
                logger.debug(f"Получение информации о пользователе: {login}")
                with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT u.user_id, u.name AS name, u.post, r.name AS role
                        FROM users u
                        INNER JOIN role r USING (role_id)
                        WHERE login = %s
                    """, (login,))
                    user = cursor.fetchone()
                    if user:
                        logger.debug(f"Данные пользователя {login} успешно получены")
                    else:
                        logger.debug(f"Пользователь {login} не найден в базе данных")
                    return user
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении данных пользователя {login}: {e}")
                return None
        else:
            logger.debug("Не удалось подключиться к базе данных для получения данных пользователя")
            return None
