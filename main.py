import pandas as pd
pd.set_option('display.max_columns', None)  # Показывать все столбцы
pd.set_option('display.width', 0)          # Устанавливать ширину вывода автоматически
pd.set_option('display.colheader_justify', 'center')  # Выравнивание заголовков колонок
pd.set_option('display.max_colwidth', None)  # Не обрезать содержимое ячеек

from db import create_connection, execute_query
from db_logic import add_data
from sql_generator import generate_sql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


if __name__ == "__main__":
    connection = create_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    table_name = "MNK.R77B00"
    search_column = "Наименование"
    search_term = "Колодки тормозные"
    group_patterns = {
        'Место установки': [r'задние', r'передние'],
        'Транспортные средства': [r'TOYOTA', r'Toyota', r'LEXUS', r'CAMRY', r'RAV4',
                                  r'MARK II', r'CALDINA', r'Nissan', r'SUBARU', r'MITSUBISHI',
                                  r'MAZDA', r'SUZUKI'],
        'Партномер': [r'[0-9a-zA-Zа-яА-Я-]+$'],
        'Тип': [r'барабанные', r'дисковые'],
        'Год': [r'[0-9]{2}-[0-9]*']
    }
    special_flags = ['Место установки', 'Транспортные средства']

    sql = generate_sql(table_name, search_column, search_term, group_patterns, special_flags)

    query_result = execute_query(connection, sql)

    print(pd.DataFrame(query_result))

    is_add_data = input("Добавить данные [Y/N]")
    if is_add_data == 'Y' or is_add_data == 'y':
        add_data(connection, query_result, search_term.replace(" ", "_"), {"article": "Артикул", "brand": "Бренд"})

    if connection:
        connection.close()