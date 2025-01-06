from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor


class DbQuery():
    @staticmethod
    def get_role(user_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        SELECT r.name
                        FROM users S
                        INNER JOIN role r USING (role_id)
                        WHERE user_id = %s
                    """, (int(user_id),))
                return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при получении статусов: {e}")
                return False
        else:
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
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                query = ("""
                        SELECT u.name AS username, u.post, r.name AS role, STRING_AGG(b.name, ', ') AS projects
                        FROM users u
                        INNER JOIN role r using(role_id)
                        INNER JOIN users_in_boards uib using(user_id)
                        INNER JOIN boards b using(board_id)
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
                print(f"Final query: {query}")
                cursor.execute(query)
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return DbQuery.formate_data(result, colnames)
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка пользователей: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def insert_new_user(name, post, login, password, role_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        insert into users
                        (name, post, login, password, role_id)
                        values(%s, %s, %s, %s, %s)
                        """, (name, post, login, generate_password_hash(password), role_id))
                cursor.connection.commit()
                print(f"Пользователь {name} добавлен")
            except psycopg2.Error as e:
                print(f"Ошибка при добавлении пользователя: {e}")
                return "Не удалось добавить пользователя"
        else:
            return "Не удалось подключиться к базе данных"