import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

class DbConnection:
    @staticmethod
    def connect_to_db():
        print(os.getenv('DBNAME'))
        try:
            # Подключение к базе данных
            print(f"Подключение к базе данных с параметрами: database=todo")
            connection = psycopg2.connect(
                dbname=os.getenv('DBNAME'),
                user=os.getenv('USER'),
                password=os.getenv('PASSWORD'),
                host=os.getenv('HOST'),
                port=os.getenv('PORT')
            )
            print("Успешное подключение к базе данных")
            return connection.cursor()
        except Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            print(f"Дополнительная информация: {str(e)}")
            print(f"Тип ошибки: {type(e).__name__}")
            return None



