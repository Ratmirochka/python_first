from db_con import DbConnection
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

class DbQuery():
    @staticmethod
    def get_payments():
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                        p.pay_id,
                        p.values,
                        u1.name AS name_who_make,
                        u2.name AS name_for_make,
                        p.date_of_pay,
                        p.date_for_period,
                        p.summ
                        FROM payments p
                        INNER JOIN users u1 ON p.who_user_id = u1.user_id
                        INNER JOIN users u2 ON p.for_user_id = u2.user_id
                        ORDER BY date_of_pay;""")
                    result = cursor.fetchall()
                    for row in result:
                        row['date_of_pay'] = row['date_of_pay'].strftime("%Y-%m-%d")
                        row['date_for_period'] = row['date_for_period'].strftime("%Y-%m-%d")
                    return result
            except psycopg2.Error as e:
                print(f"Ошибка при получении платежей: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_expenses():
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute("""
                            SELECT e.expens_id, e.values, e.date_of_exp, u1.name AS who_write,  u2.name AS who_expens, e.purpose, e.summ
                            FROM expenses e
                            INNER JOIN users u1 ON (e.who_user_id = u1.user_id)
                            INNER JOIN users u2 ON (e.for_user_id = u2.user_id)
                            ORDER BY expens_id ASC """)
                    result = cursor.fetchall()
                    for row in result:
                        row['date_of_exp'] = row['date_of_exp'].strftime("%Y-%m-%d")
                    return result
            except psycopg2.Error as e:
                print(f"Ошибка при получении трат: {e}")
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
    def get_last_sum():
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            SELECT summ FROM payments
                            WHERE pay_id = (
    	                        SELECT pay_id FROM payments
    	                        ORDER BY pay_id DESC
    	                        LIMIT 1
                            )""")
                    return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка пользователей: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def add_payment(user_id, for_user_id, value, date_for_period, last_sum):
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            INSERT INTO payments ("values", date_of_pay, who_user_id, date_for_period, for_user_id, summ)
                            VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                            """, (value, user_id, date_for_period, for_user_id, last_sum + value))
                    cursor.connection.commit()
                    return True
            except psycopg2.Error as e:
                print(f"Ошибка при добавлении платежа: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def add_expens(user_id, for_user_id, value, last_sum, purpose):
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            INSERT INTO expenses (values, date_of_exp, who_user_id, purpose, summ, for_user_id)
                            VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                            """, (value, user_id, purpose, last_sum + value, for_user_id))
                    cursor.connection.commit()
                    return True
            except psycopg2.Error as e:
                print(f"Ошибка при добвалении траты: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"

    @staticmethod
    def get_last_exp_sum():
        con = DbConnection.get_con()
        if con is not None:
            try:
                with con.cursor() as cursor:
                    cursor.execute("""
                            SELECT summ FROM expenses
                            WHERE expens_id = (
        	                    SELECT expens_id FROM expenses
        	                    ORDER BY expens_id DESC
        	                    LIMIT 1
                            )""")
                    return cursor.fetchone()
            except psycopg2.Error as e:
                print(f"Ошибка при получении списка пользователей: {e}")
                return False
        else:
            return "Не удалось подключиться к базе данных"