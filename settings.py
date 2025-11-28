from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QDoubleSpinBox, 
                             QFormLayout, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.operations import UserOperations
from utils.helpers import show_success_message, show_error_message
from utils.validators import validate_amount

class Settings(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.user_ops = UserOperations(db_manager)
        self.initUI()
        self.load_user_data()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("⚙️ Настройки")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Настройки профиля
        profile_frame = QFrame()
        profile_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 20px;
            }
        """)
        profile_layout = QVBoxLayout(profile_frame)
        
        profile_title = QLabel("👤 Настройки профиля")
        profile_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        profile_layout.addWidget(profile_title)
        
        # Форма настроек
        form_layout = QFormLayout()
        
        # Имя пользователя (только для отображения)
        self.username_label = QLabel(self.user_data['username'])
        form_layout.addRow("Имя пользователя:", self.username_label)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Введите ваш email")
        form_layout.addRow("Email:", self.email_edit)
        
        # Ежемесячный доход
        self.income_spin = QDoubleSpinBox()
        self.income_spin.setRange(0, 10000000)
        self.income_spin.setDecimals(2)
        self.income_spin.setPrefix("₽ ")
        self.income_spin.setSuffix(" в месяц")
        form_layout.addRow("Ежемесячный доход:", self.income_spin)
        
        # Тема оформления
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Тёмная"])
        form_layout.addRow("Тема оформления:", self.theme_combo)
        
        profile_layout.addLayout(form_layout)
        
        # Кнопка сохранения
        save_button = QPushButton("💾 Сохранить настройки")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        profile_layout.addWidget(save_button)
        
        layout.addWidget(profile_frame)
        
        # Информация о приложении
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("ℹ️ О приложении")
        info_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        info_layout.addWidget(info_title)
        
        app_info = QLabel("""
        <b>Финансовый советчик</b><br>
        Версия 1.0<br>
        <br>
        Приложение для управления личными финансами с интеллектуальными советами.<br>
        <br>
        Возможности:<br>
        • Учет доходов и расходов<br>
        • Постановка финансовых целей<br>
        • Визуализация финансовых данных<br>
        • Персонализированные финансовые советы<br>
        """)
        app_info.setWordWrap(True)
        app_info.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(app_info)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
    
    def load_user_data(self):
        """Загрузка данных пользователя в форму"""
        self.email_edit.setText(self.user_data.get('email', ''))
        self.income_spin.setValue(self.user_data.get('monthly_income', 0))
        
        # Устанавливаем тему
        theme = self.user_data.get('theme', 'light')
        if theme == 'dark':
            self.theme_combo.setCurrentText("Тёмная")
        else:
            self.theme_combo.setCurrentText("Светлая")
    
    def save_settings(self):
        """Сохранение настроек"""
        email = self.email_edit.text().strip()
        monthly_income = self.income_spin.value()
        theme = 'dark' if self.theme_combo.currentText() == "Тёмная" else 'light'
        
        # Обновляем настройки в базе данных
        self.user_ops.update_user_income(self.user_data['id'], monthly_income)
        self.user_ops.update_user_theme(self.user_data['id'], theme)
        
        # Обновляем email, если он изменился
        if email != self.user_data.get('email'):
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, self.user_data['id']))
            conn.commit()
            self.user_data['email'] = email
        
        # Обновляем текущие данные пользователя
        self.user_data['monthly_income'] = monthly_income
        self.user_data['theme'] = theme
        
        show_success_message(self, "Успех", "Настройки успешно сохранены!")