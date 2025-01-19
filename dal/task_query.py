from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

class DbQuery():
    @staticmethod
    def formate_data(result, colnames):
        formated_data = [
            dict(zip(colnames, row))
            for row in result
        ]
        return formated_data

    @staticmethod
    def get_user_tasks(board_id, user_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        SELECT t.task_id, t.title, t.description, t.deadline, t.start_date, t.end_date, s.name AS status_name, u.name AS responsible_name
                        FROM tasks t
                        INNER JOIN status s USING (status_id)
                        INNER JOIN responses r USING (task_id)
                        INNER JOIN users u USING (user_id)
                        WHERE t.board_id = %s AND r.user_id = %s AND t.deleted = false
                    """, (board_id, user_id))
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return DbQuery.formate_data(result, colnames)
            except psycopg2.Error as e:
                print(f"Ошибка при получении задач пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_role_in_board(user_id, board_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                                SELECT r.name 
                                FROM users_in_boards u
                                inner join role r using(role_id)
                                where user_id = %s AND board_id = %s
                    """, (user_id, board_id,))
                return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка пользователей: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

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
    def create_task(title, description, deadline, board_id, status_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        INSERT INTO tasks (title, description, deadline, start_date, board_id, status_id)
                        VALUES (%s, %s, CURRENT_DATE, %s, %s, %s)
                        RETURNING task_id
                    """, (title, description, deadline, board_id, status_id))
                task_id = cursor.fetchone()[0]
                cursor.connection.commit()
                print(f"Задача '{title}' успешно создана с ID {task_id}")
                return task_id
            except psycopg2.Error as e:
                print(f"Ошибка при создании задачи: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def assign_responsible(task_id, user_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        INSERT INTO responses (task_id, user_id)
                        VALUES (%s, %s)
                    """, (task_id, user_id))
                cursor.connection.commit()
                print(f"Пользователь {user_id} назначен ответственным за задачу {task_id}")
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при назначении ответственного: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def delete_tasks(task_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                            UPDATE tasks
                            SET deleted = true
                            WHERE task_id = %s
                        """, (task_id,))
                cursor.connection.commit()
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при получении задач пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def recover_tasks(task_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                                UPDATE tasks
                                SET deleted = false
                                WHERE task_id = %s
                            """, (task_id,))
                cursor.connection.commit()
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при получении задач пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_deleted_tasks(board_id, user_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                            SELECT t.task_id, t.title, t.description, t.deadline, t.start_date, t.end_date, s.name AS status_name, u.name AS responsible_name
                            FROM tasks t
                            INNER JOIN status s USING (status_id)
                            INNER JOIN responses r USING (task_id)
                            INNER JOIN users u USING (user_id)
                            WHERE t.board_id = %s AND r.user_id = %s AND t.deleted = true
                        """, (board_id, user_id))
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return DbQuery.formate_data(result, colnames)
            except psycopg2.Error as e:
                print(f"Ошибка при получении задач пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_status():
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("SELECT * FROM status")
                return cursor.fetchall()
            except psycopg2.Error as e:
                print(f"Ошибка при получении статусов: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def change_task_status(task_id, status_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        UPDATE tasks
                        SET status_id = %s
                        WHERE task_id = %s
                    """, (status_id, task_id))
                cursor.connection.commit()
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при изменении статуса задачи: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

