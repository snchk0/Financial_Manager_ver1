import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QCheckBox, 
                             QMessageBox, QTabWidget, QFormLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.helpers import show_error_message, show_success_message
from utils.validators import validate_email, validate_password

class AuthWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = None
        self.initUI()
        self.apply_theme('light')
    
    def initUI(self):
        self.setWindowTitle("Финансовый советчик - Авторизация")
        self.setGeometry(300, 300, 400, 500)
        self.setFixedSize(400, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Заголовок
        title_label = QLabel("Финансовый советчик")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Управляйте финансами с умом")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(30)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка входа
        self.login_tab = QWidget()
        self.setup_login_tab()
        self.tabs.addTab(self.login_tab, "Вход")
        
        # Вкладка регистрации
        self.register_tab = QWidget()
        self.setup_register_tab()
        self.tabs.addTab(self.register_tab, "Регистрация")
        
        layout.addWidget(self.tabs)
        
        # Кнопка темы
        self.theme_button = QPushButton("🌙 Тёмная тема")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        
        self.current_theme = 'light'
    
    def setup_login_tab(self):
        layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Введите имя пользователя")
        layout.addRow("Имя пользователя:", self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Введите пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", self.login_password)
        
        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.handle_login)
        layout.addRow(login_button)
        
        self.login_tab.setLayout(layout)
    
    def setup_register_tab(self):
        layout = QFormLayout()
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Придумайте имя пользователя")
        layout.addRow("Имя пользователя:", self.register_username)
        
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("example@mail.com")
        layout.addRow("Email (необязательно):", self.register_email)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Не менее 6 символов")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", self.register_password)
        
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setPlaceholderText("Повторите пароль")
        self.register_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Подтверждение:", self.register_confirm_password)
        
        register_button = QPushButton("Зарегистрироваться")
        register_button.clicked.connect(self.handle_register)
        layout.addRow(register_button)
        
        self.register_tab.setLayout(layout)
    
    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            show_error_message(self, "Ошибка", "Заполните все поля")
            return
        
        user = self.db_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            show_success_message(self, "Успех", f"Добро пожаловать, {username}!")
            self.open_main_window()
        else:
            show_error_message(self, "Ошибка", "Неверное имя пользователя или пароль")
    
    def handle_register(self):
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm_password = self.register_confirm_password.text()
        
        if not username or not password:
            show_error_message(self, "Ошибка", "Заполните обязательные поля")
            return
        
        if password != confirm_password:
            show_error_message(self, "Ошибка", "Пароли не совпадают")
            return
        
        if not validate_password(password):
            show_error_message(self, "Ошибка", "Пароль должен содержать не менее 6 символов")
            return
        
        if email and not validate_email(email):
            show_error_message(self, "Ошибка", "Введите корректный email")
            return
        
        user_id = self.db_manager.create_user(username, password, email if email else None)
        if user_id:
            show_success_message(self, "Успех", "Аккаунт успешно создан!")
            self.login_username.setText(username)
            self.login_password.setText(password)
            self.tabs.setCurrentIndex(0)
        else:
            show_error_message(self, "Ошибка", "Пользователь с таким именем уже существует")
    
    def open_main_window(self):
        from ui.main_window import MainWindow
        self.main_window = MainWindow(self.db_manager, self.current_user)
        self.main_window.show()
        self.close()
    
    def toggle_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.theme_button.setText("☀️ Светлая тема")
        else:
            self.current_theme = 'light'
            self.theme_button.setText("🌙 Тёмная тема")
        
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme):
        try:
            with open(f"assets/styles/{theme}_theme.qss", 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Файл темы не найден")