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