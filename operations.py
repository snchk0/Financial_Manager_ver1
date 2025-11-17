from database.models import DatabaseManager
from datetime import datetime, timedelta

class UserOperations:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def update_user_theme(self, user_id, theme):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET theme = ? WHERE id = ?', (theme, user_id))
        conn.commit()
    
    def update_user_income(self, user_id, income):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET monthly_income = ? WHERE id = ?', (income, user_id))
        conn.commit()

class TransactionOperations:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_transaction(self, user_id, amount, category_id, date, description, type, is_template=False):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, category_id, date, description, type, is_template)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, category_id, date, description, type, is_template))
        conn.commit()
        return cursor.lastrowid
    
    def get_user_transactions(self, user_id, start_date=None, end_date=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT t.*, c.name as category_name, c.color as category_color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        '''
        params = [user_id]
        
        if start_date and end_date:
            query += ' AND t.date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        query += ' ORDER BY t.date DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_monthly_summary(self, user_id, year, month):
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        transactions = self.get_user_transactions(user_id, start_date, end_date)
        
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        
        return {
            'income': income,
            'expenses': expenses,
            'balance': income - expenses,
            'transactions_count': len(transactions)
        }

class GoalOperations:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_goal(self, user_id, name, target_amount, deadline):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (user_id, name, target_amount, deadline)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, target_amount, deadline))
        conn.commit()
        return cursor.lastrowid
    
    def get_user_goals(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_goal_progress(self, goal_id, current_amount):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE goals SET current_amount = ? WHERE id = ?', (current_amount, goal_id))
        conn.commit()

class TemplateOperations:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_template(self, user_id, name, amount, category_id, type):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO templates (user_id, name, amount, category_id, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, amount, category_id, type))
        conn.commit()
        return cursor.lastrowid
    
    def get_user_templates(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.*, c.name as category_name
            FROM templates t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]