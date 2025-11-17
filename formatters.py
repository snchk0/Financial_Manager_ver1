def format_currency(amount):
    """Форматирование денежной суммы"""
    return f"{amount:,.2f} ₽".replace(',', ' ')

def format_percentage(value):
    """Форматирование процентного значения"""
    return f"{value:.1f}%"

def format_date(date_string):
    """Форматирование даты"""
    from datetime import datetime
    try:
        date = datetime.strptime(date_string, '%Y-%m-%d')
        return date.strftime('%d.%m.%Y')
    except:
        return date_string