import sqlite3
import bcrypt
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='financial_advisor.db'):
        self.db_path = db_path
        self.connection = None
        
    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                theme TEXT DEFAULT 'light',
                monthly_income REAL DEFAULT 0
            )
        ''')
        
        # Таблица категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                color TEXT,
                user_id INTEGER,
                is_default BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Таблица операций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                is_template BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Таблица целей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Таблица шаблонов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        conn.commit()
    
    def create_default_categories(self, user_id):
        """Создание предустановленных категорий для пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Добавляем категории доходов
        income_categories = [
            ('Зарплата', 'income', '#4CAF50'),
            ('Фриланс', 'income', '#8BC34A'),
            ('Инвестиции', 'income', '#CDDC39'),
            ('Прочее', 'income', '#FFEB3B')
        ]
        
        for name, type, color in income_categories:
            cursor.execute('''
                INSERT INTO categories (name, type, color, user_id, is_default)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, type, color, user_id, 1))
        
        # Добавляем категории расходов
        expense_categories = [
            ('Продукты', 'expense', '#F44336'),
            ('Транспорт', 'expense', '#E91E63'),
            ('Жилье', 'expense', '#9C27B0'),
            ('Развлечения', 'expense', '#673AB7'),
            ('Здоровье', 'expense', '#3F51B5'),
            ('Образование', 'expense', '#2196F3'),
            ('Одежда', 'expense', '#03A9F4'),
            ('Комунальные', 'expense', '#00BCD4'),
            ('Связь', 'expense', '#009688'),
            ('Прочее', 'expense', '#795548')
        ]
        
        for name, type, color in expense_categories:
            cursor.execute('''
                INSERT INTO categories (name, type, color, user_id, is_default)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, type, color, user_id, 1))
        
        conn.commit()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password, hashed):
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username, password, email=None):
        """Создание нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            user_id = cursor.lastrowid
            self.create_default_categories(user_id)
            
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and self.check_password(password, user['password_hash']):
            return dict(user)
        return None
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()