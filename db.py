import mysql.connector
from typing import Optional, List, Dict

from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

from logger import logger


def create_connection(host: str, user: str, password: str, database: str) -> PooledMySQLConnection | MySQLConnectionAbstract | None:
    """Функция для создания подключения к базе данных MySQL"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            ssl_disabled=True,
            use_pure=True
        )
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Ошибка подключения: {err}")
        return None


def execute_query(connection: mysql.connector.MySQLConnection, query: str) -> Optional[List[Dict[str, any]]]:
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
