from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, 
                             QComboBox, QLineEdit, QDoubleSpinBox, QFormLayout, QDialog, 
                             QDialogButtonBox, QMessageBox, QTabWidget, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database.operations import TransactionOperations, TemplateOperations
from utils.helpers import format_currency, show_error_message, show_success_message
from utils.validators import validate_amount
from datetime import datetime

class Transactions(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.transaction_ops = TransactionOperations(db_manager)
        self.template_ops = TemplateOperations(db_manager)
        self.initUI()
        self.load_transactions()
        self.load_templates()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("💰 Управление операциями")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Кнопка добавления операции
        add_button = QPushButton("➕ Добавить операцию")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.show_add_dialog)
        layout.addWidget(add_button)
        
        # Вкладки: операции и шаблоны
        self.tabs = QTabWidget()
        
        # Вкладка операций
        self.transactions_tab = QWidget()
        self.setup_transactions_tab()
        self.tabs.addTab(self.transactions_tab, "История операций")
        
        # Вкладка шаблонов
        self.templates_tab = QWidget()
        self.setup_templates_tab()
        self.tabs.addTab(self.templates_tab, "Шаблоны операций")
        
        layout.addWidget(self.tabs)
    
    def setup_transactions_tab(self):
        """Настройка вкладки с историей операций"""
        layout = QVBoxLayout(self.transactions_tab)
        
        # Таблица операций
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Дата", "Тип", "Категория", "Сумма", "Описание", "Действия"
        ])
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.transactions_table)
    
    def setup_templates_tab(self):
        """Настройка вкладки с шаблонами"""
        layout = QVBoxLayout(self.templates_tab)
        
        # Кнопка добавления шаблона
        add_template_button = QPushButton("➕ Добавить шаблон")
        add_template_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        add_template_button.clicked.connect(self.show_add_template_dialog)
        layout.addWidget(add_template_button)
        
        # Таблица шаблонов
        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(5)
        self.templates_table.setHorizontalHeaderLabels([
            "Название", "Тип", "Категория", "Сумма", "Действия"
        ])
        self.templates_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.templates_table)
    
    def load_transactions(self):
        """Загрузка операций в таблицу"""
        transactions = self.transaction_ops.get_user_transactions(self.user_data['id'])
        self.transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            # Дата
            date_item = QTableWidgetItem(transaction['date'])
            self.transactions_table.setItem(row, 0, date_item)
            
            # Тип
            type_text = "Доход" if transaction['type'] == 'income' else "Расход"
            type_item = QTableWidgetItem(type_text)
            self.transactions_table.setItem(row, 1, type_item)
            
            # Категория
            category_item = QTableWidgetItem(transaction['category_name'])
            self.transactions_table.setItem(row, 2, category_item)
            
            # Сумма
            amount_item = QTableWidgetItem(format_currency(transaction['amount']))
            self.transactions_table.setItem(row, 3, amount_item)
            
            # Описание
            desc_item = QTableWidgetItem(transaction['description'] or "")
            self.transactions_table.setItem(row, 4, desc_item)
            
            # Кнопка удаления
            delete_button = QPushButton("Удалить")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_button.clicked.connect(lambda checked, tid=transaction['id']: self.delete_transaction(tid))
            self.transactions_table.setCellWidget(row, 5, delete_button)
    
    def load_templates(self):
        """Загрузка шаблонов в таблицу"""
        templates = self.template_ops.get_user_templates(self.user_data['id'])
        self.templates_table.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            # Название
            name_item = QTableWidgetItem(template['name'])
            self.templates_table.setItem(row, 0, name_item)
            
            # Тип
            type_text = "Доход" if template['type'] == 'income' else "Расход"
            type_item = QTableWidgetItem(type_text)
            self.templates_table.setItem(row, 1, type_item)
            
            # Категория
            category_item = QTableWidgetItem(template['category_name'])
            self.templates_table.setItem(row, 2, category_item)
            
            # Сумма
            amount_item = QTableWidgetItem(format_currency(template['amount']))
            self.templates_table.setItem(row, 3, amount_item)
            
            # Кнопки
            button_layout = QHBoxLayout()
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            
            # Кнопка использования шаблона
            use_button = QPushButton("Использовать")
            use_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            use_button.clicked.connect(lambda checked, t=template: self.use_template(t))
            button_layout.addWidget(use_button)
            
            # Кнопка удаления шаблона
            delete_button = QPushButton("Удалить")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_button.clicked.connect(lambda checked, tid=template['id']: self.delete_template(tid))
            button_layout.addWidget(delete_button)
            
            self.templates_table.setCellWidget(row, 4, button_widget)
    
    def show_add_dialog(self):
        """Показать диалог добавления операции"""
        dialog = AddTransactionDialog(self.db_manager, self.user_data, self)
        if dialog.exec():
            self.load_transactions()
            show_success_message(self, "Успех", "Операция успешно добавлена!")
        self.update_dashboard()
    
    def show_add_template_dialog(self):
        """Показать диалог добавления шаблона"""
        dialog = AddTemplateDialog(self.db_manager, self.user_data, self)
        if dialog.exec():
            self.load_templates()
            show_success_message(self, "Успех", "Шаблон успешно добавлен!")
    
    def delete_transaction(self, transaction_id):
        """Удаление операции"""
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите удалить эту операцию?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
            self.load_transactions()
            show_success_message(self, "Успех", "Операция удалена!")
        
        self.update_dashboard()
    
    def delete_template(self, template_id):
        """Удаление шаблона"""
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите удалить этот шаблон?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
            conn.commit()
            self.load_templates()
            show_success_message(self, "Успех", "Шаблон удален!")
    
    def update_dashboard(self):
        """Обновление дашборда"""
        # Ищем родительское окно и обновляем дашборд
        parent = self.parent()
        while parent is not None and not hasattr(parent, 'dashboard_page'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'dashboard_page'):
            parent.dashboard_page.refresh_data()

    def use_template(self, template):
        """Использование шаблона для добавления операции"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.transaction_ops.add_transaction(
            user_id=self.user_data['id'],
            amount=template['amount'],
            category_id=template['category_id'],
            date=today,
            description=f"По шаблону: {template['name']}",
            type=template['type']
        )
        
        self.load_transactions()
        show_success_message(self, "Успех", "Операция добавлена по шаблону!")

        
        # Обновляем дашборд
        self.update_dashboard()


class AddTransactionDialog(QDialog):
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.transaction_ops = TransactionOperations(db_manager)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Добавить операцию")
        self.setFixedSize(400, 300)
        layout = QFormLayout(self)
        
        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addRow("Дата:", self.date_edit)
        
        # Тип операции
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Доход", "Расход"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Тип:", self.type_combo)
        
        # Категория
        self.category_combo = QComboBox()
        layout.addRow("Категория:", self.category_combo)
        
        # Сумма
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 1000000.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("₽ ")
        layout.addRow("Сумма:", self.amount_spin)
        
        # Описание
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Необязательное описание")
        layout.addRow("Описание:", self.desc_edit)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        # Загружаем категории
        self.load_categories()
    
    def load_categories(self):
        """Загрузка категорий в комбобокс"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name FROM categories 
            WHERE user_id = ? AND type = ?
        ''', (self.user_data['id'], 'income' if self.type_combo.currentText() == 'Доход' else 'expense'))
        
        self.category_combo.clear()
        for row in cursor.fetchall():
            self.category_combo.addItem(row['name'], row['id'])
    
    def on_type_changed(self):
        """При изменении типа операции обновляем категории"""
        self.load_categories()
    
    def accept(self):
        """Обработка принятия диалога"""
        amount = self.amount_spin.value()
        if not validate_amount(amount):
            show_error_message(self, "Ошибка", "Введите корректную сумму")
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            show_error_message(self, "Ошибка", "Выберите категорию")
            return
        
        transaction_type = 'income' if self.type_combo.currentText() == 'Доход' else 'expense'
        date = self.date_edit.date().toString('yyyy-MM-dd')
        description = self.desc_edit.text().strip()
        
        self.transaction_ops.add_transaction(
            user_id=self.user_data['id'],
            amount=amount,
            category_id=category_id,
            date=date,
            description=description,
            type=transaction_type
        )
        
        super().accept()


class AddTemplateDialog(QDialog):
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.template_ops = TemplateOperations(db_manager)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Добавить шаблон операции")
        self.setFixedSize(400, 250)
        layout = QFormLayout(self)
        
        # Название шаблона
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: Обед в столовой")
        layout.addRow("Название шаблона:", self.name_edit)
        
        # Тип операции
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Доход", "Расход"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addRow("Тип:", self.type_combo)
        
        # Категория
        self.category_combo = QComboBox()
        layout.addRow("Категория:", self.category_combo)
        
        # Сумма
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 1000000.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("₽ ")
        layout.addRow("Сумма:", self.amount_spin)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.load_categories()
    
    def load_categories(self):
        """Загрузка категорий в комбобокс"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name FROM categories 
            WHERE user_id = ? AND type = ?
        ''', (self.user_data['id'], 'income' if self.type_combo.currentText() == 'Доход' else 'expense'))
        
        self.category_combo.clear()
        for row in cursor.fetchall():
            self.category_combo.addItem(row['name'], row['id'])
    
    def on_type_changed(self):
        """При изменении типа операции обновляем категории"""
        self.load_categories()
    
    def accept(self):
        """Обработка принятия диалога"""
        name = self.name_edit.text().strip()
        if not name:
            show_error_message(self, "Ошибка", "Введите название шаблона")
            return
        
        amount = self.amount_spin.value()
        if not validate_amount(amount):
            show_error_message(self, "Ошибка", "Введите корректную сумму")
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            show_error_message(self, "Ошибка", "Выберите категорию")
            return
        
        template_type = 'income' if self.type_combo.currentText() == 'Доход' else 'expense'
        
        self.template_ops.add_template(
            user_id=self.user_data['id'],
            name=name,
            amount=amount,
            category_id=category_id,
            type=template_type
        )
        
        super().accept()