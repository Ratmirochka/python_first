from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

from loguru import logger

class DbQuery:
    @staticmethod
    def get_payments(version_id = None):
        logger.debug("Получение списка платежей")
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                        SELECT 
                        p.pay_id,
                        p.values,
                        u1.name AS name_who_make,
                        u2.name AS name_for_make,
                        p.date_of_pay,
                        p.date_for_period,
                        p.summ,
                        p.version_id
                        FROM payments p
                        INNER JOIN users u1 ON p.who_user_id = u1.user_id
                        INNER JOIN users u2 ON p.for_user_id = u2.user_id"""
                    params = []

                    if version_id is not None:
                        query += " WHERE p.version_id <= %s"
                        params.append(version_id)

                    query += " ORDER BY p.date_for_period;"
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    logger.debug(f"Данные платежей успешно получены: {result}")
                    for row in result:
                        row['date_of_pay'] = row['date_of_pay'].strftime("%Y-%m-%d")
                        row['date_for_period'] = row['date_for_period'].strftime("%Y-%m-%d")
                    return result
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении платежей: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_expenses(version_id = None):
        logger.debug("Получение списка расходов")
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                            SELECT e.expens_id, e.values, e.date_of_exp, u1.name AS who_write, u2.name AS who_expens, e.purpose, e.summ, e.version_id
                            FROM expenses e
                            INNER JOIN users u1 ON (e.who_user_id = u1.user_id)
                            INNER JOIN users u2 ON (e.for_user_id = u2.user_id)"""
                    params = []

                    if version_id is not None:
                        query += " WHERE e.version_id <= %s"
                        params.append(version_id)

                    query += " ORDER BY e.expens_id ASC;"
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                    logger.debug(f"Данные расходов успешно получены: {result}")
                    for row in result:
                        row['date_of_exp'] = row['date_of_exp'].strftime("%Y-%m-%d")
                    return result
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении трат: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_role(user_id):
        logger.debug(f"Получение роли пользователя с ID: {user_id}")
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
                logger.debug(f"Роль пользователя успешно получена: {result}")
                return result
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при получении роли пользователя: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"



    @staticmethod
    def add_payment(user_id, for_user_id, value, date_for_period):
        logger.debug(f"Добавление платежа: user_id={user_id}, for_user_id={for_user_id}, value={value}, date_for_period={date_for_period}")
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            INSERT INTO payments ("values", date_of_pay, who_user_id, date_for_period, for_user_id)
                            VALUES (%s, CURRENT_DATE, %s, %s, %s)
                            """, (value, user_id, date_for_period, for_user_id))
                    cursor.connection.commit()
                    logger.debug("Платеж успешно добавлен")
                    return True
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при добавлении платежа: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def add_expens(user_id, for_user_id, value, purpose):
        logger.debug(f"Добавление траты: user_id={user_id}, for_user_id={for_user_id}, value={value}, purpose={purpose}")
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            INSERT INTO expenses (values, date_of_exp, who_user_id, purpose, for_user_id)
                            VALUES (%s, CURRENT_DATE, %s, %s, %s)
                            """, (value, user_id, purpose, for_user_id))
                    cursor.connection.commit()
                    logger.debug("Трата успешно добавлена")
                    return True
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при добавлении траты: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_version_id():
        logger.debug(f"запрос на получение version_id")
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                                    SELECT version_id FROM versions 
                                    """)
                    return cursor.fetchall()
                    logger.debug("получили version_id")
            except psycopg2.Error as e:
                logger.debug(f"Ошибка при добавлении траты: {e}")
                return False
        else:
            logger.debug("Не удалось подключиться к базе данных")
            return "Не удалось подключиться к базе данных"

    # @staticmethod
    # def get_last_exp_sum():
    #     logger.debug("Получение последней суммы расходов")
    #     con = DbConnection.get_con()
    #     if con is not None:
    #         try:
    #             with con.cursor() as cursor:
    #                 cursor.execute("""
    #                         SELECT summ FROM expenses
    #                         WHERE expens_id = (
    #                             SELECT expens_id FROM expenses
    #                             ORDER BY expens_id DESC
    #                             LIMIT 1
    #                         )""")
    #                 result = cursor.fetchone()
    #                 logger.debug(f"Последняя сумма расходов: {result}")
    #                 return result
    #         except psycopg2.Error as e:
    #             logger.debug(f"Ошибка при получении последней суммы расходов: {e}")
    #             return False
    #     else:
    #         logger.debug("Не удалось подключиться к базе данных")
    #         return "Не удалось подключиться к базе данных"


    # @staticmethod
    # def get_last_sum():
    #     logger.debug("Получение последней суммы платежей")
    #     con = DbConnection.get_con()
    #     if con is not None:
    #         try:
    #             with con.cursor() as cursor:
    #                 cursor.execute("""
    #                         SELECT summ FROM payments
    #                         WHERE pay_id = (
    #                             SELECT pay_id FROM payments
    #                             ORDER BY pay_id DESC
    #                             LIMIT 1
    #                         )""")
    #                 result = cursor.fetchone()
    #                 logger.debug(f"Последняя сумма платежей: {result}")
    #                 return result
    #         except psycopg2.Error as e:
    #             logger.debug(f"Ошибка при получении последней суммы: {e}")
    #             return False
    #     else:
    #         logger.debug("Не удалось подключиться к базе данных")
    #         return "Не удалось подключиться к базе данных"