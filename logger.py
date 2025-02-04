import logging
import os
import subprocess

import colorlog

from datetime import datetime

import pandas as pd


def create_directory(directory: str):
    """
    Создает директорию, если она не существует.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_sql_to_file(sql: str, file_name: str) -> str:
    """
    Сохраняет SQL-запрос в файл с добавлением текущей даты и времени перед именем файла.
    Возвращает путь сохраненного файла.
    Открывает файл после сохранения в зависимости от операционной системы.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S,%f")[:-3]
    # Путь к файлу будет зависеть от операционной системы
    if os.name == 'nt':  # Windows
        directory = "sql"
    else:  # Unix-like (Linux, macOS)
        directory = "/sql"

    # Создаем директорию, если она не существует
    create_directory(directory)

    full_file_name = os.path.join(directory, f"{timestamp}_{file_name}")  # Добавляем путь и дату к имени файла

    try:
        with open(full_file_name, "w", encoding="utf-8") as file:
            file.write(sql)
        print(f"SQL-запрос успешно записан в файл '{full_file_name}'.")

        # Открываем файл после сохранения в зависимости от операционной системы
        if os.name == 'nt':  # Для Windows
            os.startfile(full_file_name)
        else:  # Для Linux/macOS
            subprocess.Popen(['xdg-open', full_file_name] if os.name == 'posix' else ['open', full_file_name])

        return full_file_name  # Возвращаем путь к файлу
    except Exception as e:
        print(f"Ошибка при записи SQL-запроса в файл: {e}")
        return ""  # В случае ошибки возвращаем пустую строку


def save_dataframe_to_file(dataframe: pd.DataFrame, file_name: str) -> str:
    """
    Сохраняет содержимое DataFrame в файл с добавлением текущей даты и времени перед именем файла.
    Возвращает путь сохраненного файла.
    Открывает файл после сохранения в зависимости от операционной системы.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S,%f")[:-3]
    # Путь к файлу будет зависеть от операционной системы
    if os.name == 'nt':  # Windows
        directory = "data_frame"
    else:  # Unix-like (Linux, macOS)
        directory = "/data_frame"

    # Создаем директорию, если она не существует
    create_directory(directory)

    full_file_name = os.path.join(directory, f"{timestamp}_{file_name}")  # Добавляем путь и дату к имени файла

    try:
        with open(full_file_name, "w", encoding="utf-8") as file:
            file.write(dataframe.to_string(index=False))
        print(f"DataFrame успешно записан в файл '{full_file_name}'.")

        # Открываем файл после сохранения в зависимости от операционной системы
        if os.name == 'nt':  # Для Windows
            os.startfile(full_file_name)
        else:  # Для Linux/macOS
            subprocess.Popen(['xdg-open', full_file_name] if os.name == 'posix' else ['open', full_file_name])

        return full_file_name  # Возвращаем путь к файлу
    except Exception as e:
        print(f"Ошибка при записи DataFrame в файл: {e}")
        return ""  # В случае ошибки возвращаем пустую строку



# Настройка логирования с цветным выводом в консоль и русской кодировкой в файл
def setup_logger():
    logger = logging.getLogger('logger')  # Создаем логер с именем 'my_logger'
    logger.setLevel(logging.DEBUG)  # Устанавливаем минимальный уровень логирования (DEBUG)

    # Формат для вывода логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)

    # Создаем обработчик для записи логов в файл с кодировкой utf-8
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)  # Записывать логи уровня INFO и выше в файл
    file_handler.setFormatter(formatter)

    # Создаем обработчик для цветного вывода логов на экран
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Выводить логи уровня DEBUG и выше на экран

    # Создаем цветной формат для консоли
    color_formatter = colorlog.ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )

    console_handler.setFormatter(color_formatter)

    # Добавляем обработчики в логер
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Пример использования логера
logger = setup_logger()

