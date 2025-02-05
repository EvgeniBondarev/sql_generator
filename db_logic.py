import mysql
from mysql.connector.pooling import PooledMySQLConnection
from typing import List, Dict, Any
import time

from config import TABLE_ATTRIBUTES, TABLE_PRODUCTS, TABLE_CATEGORIES
from db import execute_query
from logger import logger

def add_data(connection: PooledMySQLConnection, query_result: List[Dict[str, Any]], category: str, index_column: dict[str:str]):
    if "article" not in index_column and "brand" not in index_column:
        logger.error("Словарь не содержит ключи 'article' и 'brand'.")

    category_id = add_or_get_category_id(connection, category)

    total_rows = len(query_result)  # Общее количество строк
    completed_count = 0  # Счётчик выполненных операций
    start_time = time.time()  # Время начала выполнения всего цикла

    for row in query_result:
        iteration_start_time = time.time()  # Время начала выполнения одной итерации

        article = row[index_column["article"]]
        brand = row[index_column["brand"]]

        product_id = add_or_get_product_id(connection, article, brand, category_id)

        try:
            for key, value in row.items():
                if value:
                    add_or_get_attribute_id(connection, product_id, key, value)
            connection.commit()
        except:
            connection.rollback()

        completed_count += 1
        iteration_time = time.time() - iteration_start_time

        remaining_count = total_rows - completed_count  # Подсчёт оставшихся записей
        logger.info(
            f"{article}/{brand} | Выполнено: {completed_count} | Осталось: {remaining_count} | "
            f"Время итерации: {iteration_time:.2f} сек."
        )

    # Расчёт общего времени выполнения
    total_time = time.time() - start_time
    logger.info(f"Общее время выполнения: {total_time:.2f} сек.")


def add_or_get_attribute_id(
    connection: PooledMySQLConnection,
    product_id: int,
    attribute_name: str,
    attribute_value: str = None
):
    # Запрос для поиска атрибута
    select_query = f"""
        SELECT * 
        FROM {TABLE_ATTRIBUTES} 
        WHERE ProductId = {product_id} 
        AND AttributeName = '{attribute_name}'
        AND LOWER(AttributeValue) = LOWER('{attribute_value}')
    """

    # Пытаемся найти существующий атрибут
    result = execute_query(connection, select_query)

    if result:

        db_value = result[0]["AttributeValue"]
        if str(db_value).strip() != str(attribute_value).strip():
            print( str(attribute_value).strip())
            print(result)
            update_query = f"""
                    UPDATE {TABLE_ATTRIBUTES}
                    SET AttributeValue = '{attribute_value}'
                    WHERE Id = {result[0]["Id"]};
                """

            print(f"Значение атрибута '{attribute_name}' для продукта с Id {product_id} обновлено:")
            print(f"Старое значение: '{db_value}'")
            print(f"Новое значение: '{attribute_value}'")
            is_add_data = input("Обновить значение [Y/N]")
            if is_add_data == 'Y' or is_add_data == 'y' or is_add_data == 'н' or is_add_data == 'Н':
                result = execute_query(connection, update_query)
                print(f"Значение '{attribute_value}' обновлено")

        return result[0]["Id"]
    else:
        insert_query = f"""
            INSERT INTO {TABLE_ATTRIBUTES} (ProductId, AttributeName, AttributeValue) 
            VALUES ({product_id}, '{attribute_name}', {f"'{attribute_value}'" if attribute_value else 'NULL'})
        """
        try:
            # Вставляем новый атрибут
            execute_query(connection, insert_query)
            connection.commit()  # Подтверждаем изменения
            logger.warning(f"Добавлен новый атрибут '{attribute_name}' со значением '{attribute_value}' для продукта с Id {product_id}")

            # Получаем Id только что добавленного атрибута
            result = execute_query(connection, select_query)
            if result:
                return result[0]["Id"]
            else:
                logger.error(f"Не удалось получить Id для атрибута '{attribute_name}' со значением '{attribute_value}' для продукта с Id {product_id}")
                return None
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении атрибута '{attribute_name}' для продукта с Id {product_id}: {err}")
            return None


def add_or_get_product_id(
        connection: PooledMySQLConnection,
        article: str,
        brand: str,
        category_id: int = None
    ):
    select_query = f"""
        SELECT Id 
        FROM {TABLE_PRODUCTS} 
        WHERE Article = '{article}' AND Brand = '{brand}'
    """

    # Пытаемся найти существующий продукт
    result = execute_query(connection, select_query)

    if result:  # Если продукт найден
        return result[0]["Id"]
    else:
        # Запрос для добавления продукта
        insert_query = f"""
            INSERT INTO {TABLE_PRODUCTS} (Article, Brand, CategoryId) 
            VALUES ('{article}', '{brand}', {category_id if category_id else 'NULL'})
        """
        try:
            # Вставляем новый продукт
            execute_query(connection, insert_query)
            connection.commit()  # Подтверждаем изменения
            logger.warning(f"Добавлен новый продукт '{article}' бренда '{brand}'")

            # Получаем Id только что добавленного продукта
            result = execute_query(connection, select_query)
            if result:
                return result[0]["Id"]
            else:
                logger.error(f"Не удалось получить Id для продукта '{article}' бренда '{brand}'")
                return None
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении продукта '{article}' бренда '{brand}': {err}")
            return None


def add_or_get_category_id(connection: PooledMySQLConnection, category_name: str):
    # Параметризованный запрос для поиска категории
    select_query = f"SELECT Id FROM {TABLE_CATEGORIES} WHERE Name = '{category_name}'"

    # Пытаемся найти существующую категорию
    result = execute_query(connection, select_query)

    if result:  # Если категория найдена
        return result[0]["Id"]
    else:
        # Параметризованный запрос для добавления категории
        insert_query = f"INSERT INTO {TABLE_CATEGORIES} (Name) VALUES ('{category_name}')"
        try:
            # Вставляем новую категорию
            execute_query(connection, insert_query)
            connection.commit()  # Подтверждаем изменения
            logger.warning(f"Добавлена новая категория '{category_name}'")

            # Получаем Id только что добавленной категории
            result = execute_query(connection, select_query)
            if result:
                return result[0]["Id"]
            else:
                logger.error(f"Не удалось получить Id для категории '{category_name}'")
                return None
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении категории '{category_name}': {err}")
            return None
