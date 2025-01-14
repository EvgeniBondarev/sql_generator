import mysql.connector

from logger import logger


def create_connection(host, user, password, database):
    """Функция для создания подключения к базе данных MySQL"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения: {err}")
        return None

def execute_query(connection, query):
    """Функция для выполнения SQL-запросов и возврата результатов"""
    cursor = connection.cursor(dictionary=True)  # Используем dictionary для удобства работы с результатами
    try:
        cursor.execute(query)

        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        logger.error(f"Ошибка выполнения запроса: {err}")
        return None
    finally:
        cursor.close()
