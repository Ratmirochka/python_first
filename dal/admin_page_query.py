from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from loguru import logger


class DbQuery:
    @staticmethod
    def get_role(user_id):
        logger.debug(f"Получение роли для user_id: {user_id}")
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        SELECT r.name
                        FROM users S
                        INNER JOIN role r USING (role_id)
                        WHERE user_id = %s
                    """, (int(user_id),))
                result = cursor.fetchone()
                logger.debug(f"Роль успешно получена: {result}")
                return result
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении роли: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def formate_data(result, colnames):
        formated_data = [
            dict(zip(colnames, row))
            for row in result
        ]
        return formated_data

    @staticmethod
    def get_user_for_admin(filter):
        logger.debug(f"Получение пользователей для администратора с фильтром: {filter}")
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                query = ("""
                        SELECT u.name AS username, u.post, r.name AS role, STRING_AGG(b.name, ', ') AS projects
                        FROM users u
                        LEFT JOIN role r using(role_id)
                        LEFT JOIN users_in_boards uib using(user_id)
                        LEFT JOIN boards b using(board_id)
                        GROUP BY u.name, u.post, r.name
                    """)
                order_by_clauses = []
                if filter['post'] == 1:
                    order_by_clauses.append("u.post")
                if filter['role'] == 1:
                    order_by_clauses.append("r.name")
                if filter['name'] == 1:
                    order_by_clauses.append("u.name")
                if filter['project'] == 1:
                    order_by_clauses.append("4")  # Предполагаем, что это означает "project"
                if order_by_clauses:
                    query += f" ORDER BY {', '.join(order_by_clauses)}"
                cursor.execute(query)
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                formatted_data = DbQuery.formate_data(result, colnames)
                logger.debug(f"Данные пользователей успешно получены: {formatted_data}")
                return formatted_data
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении пользователей: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def insert_new_user(name, post, login, password, role_id):
        logger.debug(f"Добавление нового пользователя: name={name}, post={post}, login={login}, role_id={role_id}")
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        INSERT INTO users
                        (name, post, login, password, role_id)
                        VALUES (%s, %s, %s, %s, %s)
                        """, (name, post, login, generate_password_hash(password), role_id))
                cursor.connection.commit()
                logger.debug(f"Пользователь {name} успешно добавлен")
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при добавлении пользователя: {e}")
                return "Не удалось добавить пользователя"
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"