import logging
import colorlog

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

