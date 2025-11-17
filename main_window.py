import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QListWidget,
                             QListWidgetItem, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.operations import UserOperations
from ui.dashboard import Dashboard
from ui.transactions import Transactions
from ui.goals import Goals
from ui.analytics import Analytics
from ui.advice import Advice
from ui.settings import Settings
from utils.helpers import show_success_message

class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.user_ops = UserOperations(db_manager)
        self.current_theme = user_data.get('theme', 'light')
        self.initUI()
        self.apply_theme(self.current_theme)
    
    def initUI(self):
        self.setWindowTitle(f"Финансовый советчик - {self.user_data['username']}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Боковая панель навигации
        self.setup_sidebar(main_layout)
        
        # Основная область контента
        self.setup_content_area(main_layout)
        
        # По умолчанию показываем дашборд
        self.nav_list.setCurrentRow(0)
    
    def setup_sidebar(self, main_layout):
        """Настройка боковой панели"""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Заголовок
        title_label = QLabel("Финансовый\nсоветчик")
        title_label.setStyleSheet("""
            QLabel {
                color: white; 
                font-size: 18px; 
                font-weight: bold; 
                padding: 20px;
                background-color: #34495e;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(80)
        sidebar_layout.addWidget(title_label)
        
        # Список разделов
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 15px 20px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                border-left: 4px solid #2980b9;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        
        # Элементы навигации
        nav_items = [
            "📊 Дашборд",
            "💰 Операции", 
            "🎯 Цели",
            "📈 Аналитика",
            "💡 Советы",
            "⚙️ Настройки"
        ]
        
        for item in nav_items:
            list_item = QListWidgetItem(item)
            list_item.setSizeHint(self.nav_list.sizeHint())
            self.nav_list.addItem(list_item)
        
        self.nav_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.nav_list)
        
        # Информация о пользователе
        user_info = QLabel(f"👤 {self.user_data['username']}")
        user_info.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                padding: 15px;
                border-top: 1px solid #34495e;
                font-size: 12px;
            }
        """)
        sidebar_layout.addWidget(user_info)
        
        # Кнопка выхода
        logout_button = QPushButton("🚪 Выйти")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px;
                font-weight: bold;
                margin: 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_button.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_button)
        
        main_layout.addWidget(sidebar)
    
    def setup_content_area(self, main_layout):
        """Настройка области контента"""
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Приветствие
        welcome_label = QLabel(f"Добро пожаловать, {self.user_data['username']}! 👋")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_bar_layout.addWidget(welcome_label)
        
        top_bar_layout.addStretch()
        
        # Кнопка темы
        self.theme_button = QPushButton()
        self.update_theme_button_text()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        top_bar_layout.addWidget(self.theme_button)
        
        content_layout.addWidget(top_bar)
        
        # Область страниц
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Инициализация страниц
        self.setup_pages()
        
        # Подключаем обновление при переключении страниц
        self.stacked_widget.currentChanged.connect(self.on_page_changed)
        
        main_layout.addWidget(content_area, 1)
    
    def setup_pages(self):
        """Инициализация всех страниц приложения"""
        # Дашборд
        self.dashboard_page = Dashboard(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Операции
        self.transactions_page = Transactions(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.transactions_page)
        
        # Цели
        self.goals_page = Goals(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.goals_page)
        
        # Аналитика
        self.analytics_page = Analytics(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.analytics_page)
        
        # Советы
        self.advice_page = Advice(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.advice_page)
        
        # Настройки
        self.settings_page = Settings(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.settings_page)
    
    def change_page(self, index):
        """Смена страницы - ЭТОТ МЕТОД БЫЛ ОТСУТСТВОВАЛ"""
        if index >= 0 and index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
    
    def toggle_theme(self):
        """Переключение темы"""
        if self.current_theme == 'light':
            self.current_theme = 'dark'
        else:
            self.current_theme = 'light'
        
        self.update_theme_button_text()
        self.apply_theme(self.current_theme)
        self.user_ops.update_user_theme(self.user_data['id'], self.current_theme)
        show_success_message(self, "Успех", f"Тема изменена на {'тёмную' if self.current_theme == 'dark' else 'светлую'}")
    
    def update_theme_button_text(self):
        """Обновление текста кнопки темы"""
        if self.current_theme == 'light':
            self.theme_button.setText("🌙 Тёмная тема")
        else:
            self.theme_button.setText("☀️ Светлая тема")
    
    def apply_theme(self, theme):
        """Применение темы"""
        try:
            with open(f"assets/styles/{theme}_theme.qss", 'r', encoding='utf-8') as f:
                style = f.read()
            self.setStyleSheet(style)
        except FileNotFoundError:
            print(f"Файл темы {theme}_theme.qss не найден")
    
    def logout(self):
        """Выход из аккаунта"""
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   'Вы уверены, что хотите выйти?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            from ui.auth_window import AuthWindow
            self.auth_window = AuthWindow(self.db_manager)
            self.auth_window.show()
            self.close()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db_manager.close()
        event.accept()

    def on_page_changed(self, index):
        """Обновление данных при переключении страниц"""
        current_widget = self.stacked_widget.widget(index)
        
        # Обновляем дашборд при переходе на него
        if current_widget == self.dashboard_page and hasattr(self.dashboard_page, 'refresh_data'):
            self.dashboard_page.refresh_data()
        
        # Обновляем страницу операций при переходе на нее
        if current_widget == self.transactions_page and hasattr(self.transactions_page, 'load_transactions'):
            self.transactions_page.load_transactions()
            self.transactions_page.load_templates()
        
        # Обновляем страницу целей при переходе на нее
        if current_widget == self.goals_page and hasattr(self.goals_page, 'load_goals'):
            self.goals_page.load_goals()
        
        # Обновляем страницу аналитики при переходе на нее
        if current_widget == self.analytics_page and hasattr(self.analytics_page, 'load_data'):
            self.analytics_page.load_data()
        
        # Обновляем страницу советов при переходе на нее
        if current_widget == self.advice_page and hasattr(self.advice_page, 'load_advice'):
            self.advice_page.load_advice()