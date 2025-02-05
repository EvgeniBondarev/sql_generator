import traceback
from db import create_connection
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, TABLE_CATEGORIES, TABLE_PRODUCTS, TABLE_ATTRIBUTES
from logger import logger

def create_tables():
    """Создаёт таблицы в базе данных, если они не существуют."""
    connection = create_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    if connection is None:
        logger.error("Не удалось подключиться к базе данных для создания таблиц")
        return

    cursor = connection.cursor()
    try:
        # Создание таблицы категорий
        query_categories = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_CATEGORIES} (
                Id INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(100) NOT NULL UNIQUE
            );
        """
        cursor.execute(query_categories)
        logger.info(f"Таблица {TABLE_CATEGORIES} создана или уже существует")

        # Создание таблицы товаров
        query_products = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_PRODUCTS} (
                Id INT PRIMARY KEY AUTO_INCREMENT,
                Article VARCHAR(50) NOT NULL,
                Brand VARCHAR(50) NOT NULL,
                CategoryId INT,
                FOREIGN KEY (CategoryId) REFERENCES {TABLE_CATEGORIES}(Id) ON DELETE SET NULL
            );
        """
        cursor.execute(query_products)
        logger.info(f"Таблица {TABLE_PRODUCTS} создана или уже существует")

        # Создание таблицы атрибутов
        query_attributes = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_ATTRIBUTES} (
                Id INT PRIMARY KEY AUTO_INCREMENT,
                ProductId INT NOT NULL,
                AttributeName VARCHAR(50) NOT NULL,
                AttributeValue TEXT,
                FOREIGN KEY (ProductId) REFERENCES {TABLE_PRODUCTS}(Id) ON DELETE CASCADE
            );
        """
        cursor.execute(query_attributes)
        logger.info(f"Таблица {TABLE_ATTRIBUTES} создана или уже существует")

        connection.commit()
        logger.info("Все таблицы успешно созданы или уже существуют")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}\n{traceback.format_exc()}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
