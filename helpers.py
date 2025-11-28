from PyQt6.QtWidgets import QMessageBox

def show_error_message(parent, title, message):
    """Показать сообщение об ошибке"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()

def show_success_message(parent, title, message):
    """Показать сообщение об успехе"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()

def show_warning_message(parent, title, message):
    """Показать предупреждение"""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec()

def format_currency(amount):
    """Форматирование денежной суммы"""
    return f"{amount:,.2f} ₽".replace(',', ' ')

def format_percentage(value):
    """Форматирование процентного значения"""
    return f"{value:.1f}%"

def validate_email(email):
    """Простая валидация email"""
    return '@' in email and '.' in email

def validate_password(password):
    """Валидация пароля"""
    return len(password) >= 6

def validate_amount(amount):
    """Валидация суммы"""
    try:
        return float(amount) > 0
    except (ValueError, TypeError):
        return False