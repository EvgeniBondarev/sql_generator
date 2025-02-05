import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QGroupBox, QFormLayout, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QFileDialog
import traceback
import pandas as pd
import sys

from logger import save_sql_to_file, save_dataframe_to_file
from db import create_connection, execute_query
from db_logic import add_data
from sql_generator import generate_sql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from logger import logger



class SQLGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Генератор SQL-запросов")
        self.setGeometry(100, 100, 800, 600)

        self.group_patterns = {}
        self.special_flags_vars = []

        self.init_ui()

    def init_ui(self):
        # Layouts
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        group_layout = QVBoxLayout()
        special_flags_layout = QVBoxLayout()
        special_key_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Имя таблицы
        self.table_name_input = QLineEdit(self)
        self.table_name_input.setPlaceholderText("MNK.R77B00")
        form_layout.addRow(QLabel("Имя таблицы:"), self.table_name_input)

        # Колонка для поиска
        self.search_column_input = QLineEdit(self)
        self.search_column_input.setPlaceholderText("Наименование")
        form_layout.addRow(QLabel("Колонка для поиска:"), self.search_column_input)

        # Поисковый термин
        self.search_term_input = QLineEdit(self)
        self.search_term_input.setPlaceholderText("Колодки тормозные")
        form_layout.addRow(QLabel("Поисковый термин:"), self.search_term_input)

        # Групповые шаблоны
        group_box = QGroupBox("Групповые шаблоны")
        group_box.setLayout(group_layout)

        self.group_name_input = QLineEdit(self)
        self.patterns_input = QLineEdit(self)
        add_group_btn = QPushButton("Добавить группу", self)
        add_group_btn.clicked.connect(self.add_group)

        group_layout.addWidget(QLabel("Название группы:"))
        group_layout.addWidget(self.group_name_input)
        group_layout.addWidget(QLabel("Шаблоны (через запятую):"))
        group_layout.addWidget(self.patterns_input)
        group_layout.addWidget(add_group_btn)

        self.groups_list_widget = QTableWidget(self)
        self.groups_list_widget.setColumnCount(2)
        self.groups_list_widget.setHorizontalHeaderLabels(['Название группы', 'Шаблоны'])
        group_layout.addWidget(self.groups_list_widget)

        # Специальные флаги
        special_flags_box = QGroupBox("Специальные флаги")
        special_flags_box.setLayout(special_flags_layout)

        self.special_flags_input = QLineEdit(self)
        self.special_flags_input.setPlaceholderText("Флаги (через запятую)")

        special_flags_layout.addWidget(QLabel("Специальные флаги:"))
        special_flags_layout.addWidget(self.special_flags_input)

        # Специальные ключи
        special_key_box = QGroupBox("Специальные ключи")
        special_key_box.setLayout(special_key_layout)
        self.special_key_lable = QLabel(self)
        special_key_layout.addWidget(self.special_key_lable)

        # Кнопки
        generate_sql_btn = QPushButton("Сгенерировать SQL", self)
        generate_sql_btn.clicked.connect(self.generate)
        self.add_data_btn = QPushButton("Добавить данные", self)
        self.add_data_btn.setEnabled(False)
        self.add_data_btn.clicked.connect(self.add_data)

        button_layout.addWidget(generate_sql_btn)
        button_layout.addWidget(self.add_data_btn)

        # Кнопка загрузки JSON
        load_preset_btn = QPushButton("Загрузить пресет", self)
        load_preset_btn.clicked.connect(self.load_preset)
        button_layout.addWidget(load_preset_btn)

        # Область результатов (с прокруткой)
        self.result_area = QScrollArea(self)
        self.result_area.setWidgetResizable(True)
        self.result_text_area = QTableWidget(self)
        self.result_area.setWidget(self.result_text_area)

        # Добавляем виджеты в основной layout
        layout.addLayout(form_layout)
        layout.addWidget(group_box)
        layout.addWidget(special_flags_box)
        layout.addWidget(special_key_box)
        layout.addLayout(button_layout)
        layout.addWidget(self.result_area)

        self.setLayout(layout)

    def add_group(self):
        group_name = self.group_name_input.text()
        patterns = [p.strip() for p in self.patterns_input.text().split(',') if p.strip()]

        if not group_name or not patterns:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, заполните название группы и шаблоны")
            return

        self.group_patterns[group_name] = patterns
        row_position = self.groups_list_widget.rowCount()
        self.groups_list_widget.insertRow(row_position)
        self.groups_list_widget.setItem(row_position, 0, QTableWidgetItem(group_name))
        self.groups_list_widget.setItem(row_position, 1, QTableWidgetItem(', '.join(patterns)))

        self.group_name_input.clear()
        self.patterns_input.clear()

    def update_special_flags(self):
        # Разделяем введенные флаги через запятую
        special_flags = [flag.strip() for flag in self.special_flags_input.text().split(',') if flag.strip()]
        self.special_flags_vars = special_flags

    def validate_input(self):
        if not self.table_name_input.text().strip():
            QMessageBox.critical(self, "Ошибка", "Имя таблицы обязательно")
            return False
        if not self.search_column_input.text().strip():
            QMessageBox.critical(self, "Ошибка", "Колонка для поиска обязательна")
            return False
        if not self.search_term_input.text().strip():
            QMessageBox.critical(self, "Ошибка", "Поисковый термин обязателен")
            return False
        if not self.group_patterns:
            QMessageBox.critical(self, "Ошибка", "Необходимо добавить хотя бы одну группу")
            return False
        return True

    def generate(self):
        if not self.validate_input():
            return

        connection = None
        try:
            connection = create_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            logger.info("Connect:")
            logger.info(DB_HOST)
            logger.info(DB_USER)
            logger.info('*' * len(DB_PASSWORD))
            logger.info(DB_NAME)


            self.update_special_flags()

            sql = generate_sql(
                table_name=self.table_name_input.text(),
                search_column=self.search_column_input.text(),
                search_term=self.search_term_input.text(),
                group_patterns=self.group_patterns,
                special_flags=self.special_flags_vars
            )

            save_sql_to_file(sql, "generated_query.sql")
            query_result = execute_query(connection, sql)

            self.query_result = query_result
            self.df = pd.DataFrame(query_result)
            save_dataframe_to_file(self.df, "query_result.txt")

            # Обновление таблицы результатов
            self.result_text_area.setRowCount(len(self.df))
            self.result_text_area.setColumnCount(len(self.df.columns))
            self.result_text_area.setHorizontalHeaderLabels(self.df.columns.tolist())

            for row in range(len(self.df)):
                for col, column in enumerate(self.df.columns):
                    self.result_text_area.setItem(row, col, QTableWidgetItem(str(self.df.iloc[row, col])))

            self.add_data_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"Ошибка при генерации SQL: {e}\n{traceback.format_exc()}")
            traceback.print_exc()  # Вывод ошибки в консоль
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if connection:
                connection.close()

    def add_data(self):
        try:
            connection = create_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

            add_data(
                connection=connection,
                query_result=self.query_result,
                category=self.search_term_input.text().replace(" ", "_"),
                index_column=self.keys
            )

            QMessageBox.information(self, "Успех", "Данные успешно добавлены")
        except Exception as e:
            logger.error(f"Ошибка при добавлении данных: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if connection:
                connection.close()

    def load_preset(self):
        # Открытие диалога выбора файла
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]

            # Чтение данных из JSON-файла
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    preset = json.load(file)

                if "keys" not in preset or not all(k in preset["keys"] for k in {"article": "Артикул", "brand": "Бренд"}):
                    error_message = "Ошибка: отсутствуют обязательные ключи 'article' и 'brand' в пресете."
                    logger.error(error_message)
                    QMessageBox.information(None, "Ошибка", error_message)
                    return None


                # Заполнение полей
                self.table_name_input.setText(preset.get("table_name", ""))
                self.search_column_input.setText(preset.get("search_column", ""))
                self.search_term_input.setText(preset.get("search_term", ""))
                self.keys = preset.get("keys", {})

                keys = preset.get("keys", {})
                text = ", ".join(keys.values()) if isinstance(keys, dict) else str(keys)
                self.special_key_lable.setText(text)

                # Групповые шаблоны
                self.group_patterns = preset.get("group_patterns", {})
                self.special_flags_input.setText(', '.join(preset.get("special_flags", [])))

                self.update_ui_for_groups()

                logger.info(f"Пресет загружен: {preset}")

            except Exception as e:
                logger.error(f"Ошибка при загрузке пресета из файла: {e}\n{traceback.format_exc()}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пресет: {str(e)}")

    def update_ui_for_groups(self):
        # Обновление UI для групп
        self.groups_list_widget.setRowCount(0)
        for group_name, patterns in self.group_patterns.items():
            row_position = self.groups_list_widget.rowCount()
            self.groups_list_widget.insertRow(row_position)
            self.groups_list_widget.setItem(row_position, 0, QTableWidgetItem(group_name))
            self.groups_list_widget.setItem(row_position, 1, QTableWidgetItem(', '.join(patterns)))


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = SQLGeneratorApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}\n{traceback.format_exc()}")