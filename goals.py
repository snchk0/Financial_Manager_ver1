from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, 
                             QLineEdit, QDoubleSpinBox, QFormLayout, QDialog, 
                             QDialogButtonBox, QMessageBox, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database.operations import GoalOperations
from utils.helpers import format_currency, show_error_message, show_success_message
from utils.validators import validate_amount
from datetime import datetime

class Goals(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.goal_ops = GoalOperations(db_manager)
        self.initUI()
        self.load_goals()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("🎯 Финансовые цели")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Описание
        desc = QLabel("Ставьте финансовые цели и отслеживайте прогресс их достижения")
        desc.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(desc)
        
        # Кнопка добавления цели
        add_button = QPushButton("➕ Добавить цель")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        add_button.clicked.connect(self.show_add_dialog)
        layout.addWidget(add_button)
        
        # Таблица целей
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(6)
        self.goals_table.setHorizontalHeaderLabels([
            "Название", "Целевая сумма", "Текущий прогресс", "Прогресс", "Дедлайн", "Действия"
        ])
        self.goals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.goals_table)
    
    def load_goals(self):
        """Загрузка целей в таблицу"""
        goals = self.goal_ops.get_user_goals(self.user_data['id'])
        self.goals_table.setRowCount(len(goals))
        
        for row, goal in enumerate(goals):
            # Название
            name_item = QTableWidgetItem(goal['name'])
            self.goals_table.setItem(row, 0, name_item)
            
            # Целевая сумма
            target_item = QTableWidgetItem(format_currency(goal['target_amount']))
            self.goals_table.setItem(row, 1, target_item)
            
            # Текущий прогресс
            progress_text = f"{format_currency(goal['current_amount'])} ({goal['current_amount']/goal['target_amount']*100:.1f}%)"
            progress_item = QTableWidgetItem(progress_text)
            self.goals_table.setItem(row, 2, progress_item)
            
            # Прогресс-бар
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(goal['current_amount'] / goal['target_amount'] * 100))
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 4px;
                }
            """)
            self.goals_table.setCellWidget(row, 3, progress_bar)
            
            # Дедлайн
            deadline = goal['deadline'] or "Не установлен"
            deadline_item = QTableWidgetItem(deadline)
            self.goals_table.setItem(row, 4, deadline_item)
            
            # Кнопки
            button_layout = QHBoxLayout()
            button_widget = QWidget()
            button_widget.setLayout(button_layout)
            
            # Кнопка добавления средств
            add_money_button = QPushButton("➕")
            add_money_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            add_money_button.clicked.connect(lambda checked, gid=goal['id']: self.show_add_money_dialog(gid))
            button_layout.addWidget(add_money_button)
            
            # Кнопка удаления
            delete_button = QPushButton("🗑️")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_button.clicked.connect(lambda checked, gid=goal['id']: self.delete_goal(gid))
            button_layout.addWidget(delete_button)
            
            self.goals_table.setCellWidget(row, 5, button_widget)
    
    def show_add_dialog(self):
        """Показать диалог добавления цели"""
        dialog = AddGoalDialog(self.db_manager, self.user_data, self)
        if dialog.exec():
            self.load_goals()
            show_success_message(self, "Успех", "Цель успешно добавлена!")
    
    def show_add_money_dialog(self, goal_id):
        """Показать диалог добавления средств к цели"""
        dialog = AddMoneyDialog(self.db_manager, goal_id, self)
        if dialog.exec():
            self.load_goals()
            show_success_message(self, "Успех", "Средства успешно добавлены к цели!")
    
    def delete_goal(self, goal_id):
        """Удаление цели"""
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите удалить эту цель?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            conn.commit()
            self.load_goals()
            show_success_message(self, "Успех", "Цель удалена!")


class AddGoalDialog(QDialog):
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data
        self.goal_ops = GoalOperations(db_manager)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Добавить финансовую цель")
        self.setFixedSize(400, 250)
        layout = QFormLayout(self)
        
        # Название цели
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: Накопить на отпуск")
        layout.addRow("Название цели:", self.name_edit)
        
        # Целевая сумма
        self.target_spin = QDoubleSpinBox()
        self.target_spin.setRange(0.01, 10000000.00)
        self.target_spin.setDecimals(2)
        self.target_spin.setPrefix("₽ ")
        layout.addRow("Целевая сумма:", self.target_spin)
        
        # Дедлайн
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate().addMonths(6))  # По умолчанию +6 месяцев
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setMinimumDate(QDate.currentDate().addDays(1))
        layout.addRow("Дедлайн:", self.deadline_edit)
        
        # Начальный взнос
        self.initial_spin = QDoubleSpinBox()
        self.initial_spin.setRange(0.00, 10000000.00)
        self.initial_spin.setDecimals(2)
        self.initial_spin.setPrefix("₽ ")
        self.initial_spin.setValue(0.00)
        layout.addRow("Начальный взнос:", self.initial_spin)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def accept(self):
        """Обработка принятия диалога"""
        name = self.name_edit.text().strip()
        if not name:
            show_error_message(self, "Ошибка", "Введите название цели")
            return
        
        target_amount = self.target_spin.value()
        if not validate_amount(target_amount):
            show_error_message(self, "Ошибка", "Введите корректную целевую сумму")
            return
        
        initial_amount = self.initial_spin.value()
        if initial_amount < 0:
            show_error_message(self, "Ошибка", "Начальный взнос не может быть отрицательным")
            return
        
        deadline = self.deadline_edit.date().toString('yyyy-MM-dd')
        
        goal_id = self.goal_ops.add_goal(
            user_id=self.user_data['id'],
            name=name,
            target_amount=target_amount,
            deadline=deadline
        )
        
        # Если указан начальный взнос, добавляем его
        if initial_amount > 0:
            self.goal_ops.update_goal_progress(goal_id, initial_amount)
        
        super().accept()


class AddMoneyDialog(QDialog):
    def __init__(self, db_manager, goal_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.goal_id = goal_id
        self.goal_ops = GoalOperations(db_manager)
        self.initUI()
        self.load_goal_info()
    
    def initUI(self):
        self.setWindowTitle("Добавить средства к цели")
        self.setFixedSize(350, 200)
        layout = QFormLayout(self)
        
        # Информация о цели
        self.goal_info = QLabel()
        self.goal_info.setWordWrap(True)
        layout.addRow(self.goal_info)
        
        # Сумма для добавления
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 1000000.00)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("₽ ")
        layout.addRow("Сумма для добавления:", self.amount_spin)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def load_goal_info(self):
        """Загрузка информации о цели"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM goals WHERE id = ?', (self.goal_id,))
        goal = cursor.fetchone()
        
        if goal:
            progress = (goal['current_amount'] / goal['target_amount']) * 100
            info_text = f"Цель: {goal['name']}\nПрогресс: {format_currency(goal['current_amount'])} / {format_currency(goal['target_amount'])} ({progress:.1f}%)"
            self.goal_info.setText(info_text)
    
    def accept(self):
        """Обработка принятия диалога"""
        amount = self.amount_spin.value()
        if not validate_amount(amount):
            show_error_message(self, "Ошибка", "Введите корректную сумму")
            return
        
        # Получаем текущий прогресс
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT current_amount FROM goals WHERE id = ?', (self.goal_id,))
        current_amount = cursor.fetchone()['current_amount']
        
        # Обновляем прогресс
        new_amount = current_amount + amount
        self.goal_ops.update_goal_progress(self.goal_id, new_amount)
        
        super().accept()