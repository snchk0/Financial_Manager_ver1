import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.auth_window import AuthWindow
from database.models import DatabaseManager

def main():
    # Настройки для HiRes экранов
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Финансовый советчик")
    app.setApplicationVersion("1.0")
    
    # Инициализация базы данных
    db_manager = DatabaseManager()
    db_manager.init_database()
    
    # Запуск окна авторизации
    auth_window = AuthWindow(db_manager)
    auth_window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()