import re

def is_regex(pattern):
    regex_characters = {'[', ']', '{', '}', '\\', '*', '+', '?', '^', '$', '|', '(', ')', '.'}
    if any(char in pattern for char in regex_characters):
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
    return False

def generate_with_sql(group_patterns: dict[str, list[str]]):
    sql = "WITH "

    for group_name, patterns in group_patterns.items():

        sql += f"{group_name.replace(' ', '_')} AS (\n"
        for i, pattern in enumerate(patterns):
            if i == 0:
                sql += f"    SELECT '{pattern}' AS {group_name.replace(' ', '_')}\n"
            else:
                sql += f"    UNION ALL SELECT '{pattern}'\n"
        sql += "),\n"

    sql = sql.rstrip(",\n") + "\n"

    return sql

def generate_sql(table_name: str, search_column: str, search_term: str, group_patterns: dict[str, list[str]], special_flags: list[str]):
    sql = ""
    if special_flags:
        sql += generate_with_sql({key: value for key, value in group_patterns.items() if key in special_flags})
        group_patterns = {key: value for key, value in group_patterns.items() if key not in special_flags}

    sql += f"SELECT *,\n"

    total_groups = len(group_patterns)
    for i, (group_name, patterns) in enumerate(group_patterns.items(), start=1):
        sql += "\tCASE\n"

        for pattern in patterns:
            if is_regex(pattern):
                sql += f"\t\tWHEN {search_column} REGEXP '{pattern}' THEN CONCAT(REGEXP_SUBSTR({search_column}, '{pattern}'))\n"
            else:
                sql += f"\t\tWHEN {search_column} REGEXP '{pattern}' THEN '{pattern}'\n"

        sql += "\t\tELSE null\n"
        if i == total_groups:
            sql += f"\tEND AS '{group_name}'\n"
        else:
            sql += f"\tEND AS '{group_name}',\n"

    sql += f"FROM {table_name}\n"

    if special_flags:
        for special_flag in special_flags:
            sql += f"JOIN {special_flag.replace(' ', '_')} {special_flag.replace(' ', '_')}\n"
            sql += f"\t\tON {search_column.replace(' ', '_')} REGEXP {special_flag.replace(' ', '_')}.{special_flag.replace(' ', '_')}\n"

    sql += f"WHERE LOWER({search_column}) LIKE LOWER('%{search_term}%');"

    return sql

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

generate_sql(table_name, search_column, search_term, group_patterns, special_flags)
