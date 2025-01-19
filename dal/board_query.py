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
    def get_user_boards(user_id, deleted_boards):
        cursor = DbConnection.connect_to_db()
        print(f"deleted = {deleted_boards}")
        if cursor is not None:
            try:
                query = """
                        SELECT b.board_id, b.name, b.description, r.name AS role_name
                        FROM boards b
                        INNER JOIN users_in_boards uib USING (board_id)
                        INNER JOIN role r ON uib.role_id = r.role_id
                        WHERE uib.user_id = %s 
                    """
                if deleted_boards == True:
                    query += " AND b.deleted = true"
                else: query += " AND b.deleted = false"
                print(query)
                cursor.execute(query, (user_id,))
                result = cursor.fetchall()
                print(result)
                colnames = [desc[0] for desc in cursor.description]
                return DbQuery.formate_data(result, colnames)
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка досок пользователя: {e}")
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
    def add_board(name, description):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        INSERT INTO boards (name, description)
                        VALUES (%s, %s)
                        RETURNING board_id
                    """, (name, description))
                board_id = cursor.fetchone()[0]
                cursor.connection.commit()
                return board_id
            except psycopg2.Error as e:
                print(f"Ошибка при добавлении доски: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def add_user_to_board(board_id, user_id, role_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        INSERT INTO users_in_boards (board_id, user_id, role_id)
                        VALUES (%s, %s, %s)
                    """, (board_id, user_id, role_id))
                cursor.connection.commit()
                print(f"Пользователь {user_id} успешно добавлен в доску {board_id}")
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при добавлении пользователя в доску: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def delete_board(board_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                                UPDATE boards
                                SET deleted = true
                                WHERE board_id = %s
                            """, (board_id,))
                cursor.connection.commit()
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при удалении задачи: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def recover_board(board_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                                UPDATE board
                                SET deleted = false
                                WHERE board_id = %s
                            """, (board_id,))
                cursor.connection.commit()
                return True
            except psycopg2.Error as e:
                print(f"Ошибка при удалении задачи: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_deleted_boards(user_id):
        cursor = DbConnection.connect_to_db()
        if cursor is not None:
            try:
                cursor.execute("""
                        SELECT b.board_id, b.name, b.description, r.name AS role_name
                        FROM boards b
                        INNER JOIN users_in_boards uib USING (board_id)
                        INNER JOIN role r ON uib.role_id = r.role_id
                        WHERE uib.user_id = %s AND b.deleted = true
                    """, (user_id,))
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                return DbQuery.formate_data(result, colnames)
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка досок пользователя: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    # @staticmethod
    # def get_role_in_board(user_id, board_id):
    #     cursor = DbConnection.connect_to_db()
    #     if cursor is not None:
    #         try:
    #             cursor.execute("""
    #                                 SELECT r.name
    #                                 FROM users_in_boards u
    #                                 inner join role r using(role_id)
    #                                 where user_id = %s AND board_id = %s
    #                     """, (user_id, board_id,))
    #             return cursor.fetchone()
    #         except psycopg2.Error as e:
    #             print(f"Ошибка при получении списка пользователей: {e}")
    #             return False
    #     else:
    #         return "Не удалось подключиться к базе данных"