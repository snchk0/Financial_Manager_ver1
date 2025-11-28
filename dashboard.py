from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.operations import TransactionOperations, GoalOperations
from core.analytics import FinancialAnalytics
from core.advisor import FinancialAdvisor
from utils.helpers import format_currency
from datetime import datetime, timedelta

class Dashboard(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.transaction_ops = TransactionOperations(db_manager)
        self.goal_ops = GoalOperations(db_manager)
        self.analytics = FinancialAnalytics(db_manager, user_data['id'])
        self.advisor = FinancialAdvisor(db_manager, user_data['id'])
        self.initUI()
        self.load_data()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("📊 Обзор финансов")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Прокручиваемая область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Быстрая статистика
        self.setup_quick_stats(scroll_layout)
        
        # Последние операции
        self.setup_recent_transactions(scroll_layout)
        
        # Финансовые советы
        self.setup_advice_section(scroll_layout)
        
        # Цели
        self.setup_goals_section(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def setup_quick_stats(self, layout):
        """Быстрая статистика"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📈 Статистика за текущий месяц")
        stats_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_layout.addWidget(stats_title)
        
        # Сетка для показателей
        grid_layout = QGridLayout()
        
        # Доходы
        self.income_label = QLabel("0.00 ₽")
        self.income_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.income_label.setStyleSheet("color: #4CAF50;")
        grid_layout.addWidget(QLabel("Доходы:"), 0, 0)
        grid_layout.addWidget(self.income_label, 0, 1)
        
        # Расходы
        self.expenses_label = QLabel("0.00 ₽")
        self.expenses_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.expenses_label.setStyleSheet("color: #F44336;")
        grid_layout.addWidget(QLabel("Расходы:"), 1, 0)
        grid_layout.addWidget(self.expenses_label, 1, 1)
        
        # Баланс
        self.balance_label = QLabel("0.00 ₽")
        self.balance_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: #2196F3;")
        grid_layout.addWidget(QLabel("Баланс:"), 2, 0)
        grid_layout.addWidget(self.balance_label, 2, 1)
        
        stats_layout.addLayout(grid_layout)
        layout.addWidget(stats_frame)
    
    def setup_recent_transactions(self, layout):
        """Последние операции"""
        transactions_frame = QFrame()
        transactions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        transactions_layout = QVBoxLayout(transactions_frame)
        
        transactions_title = QLabel("💳 Последние операции")
        transactions_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        transactions_layout.addWidget(transactions_title)
        
        self.transactions_content = QLabel("Операций пока нет")
        self.transactions_content.setWordWrap(True)
        transactions_layout.addWidget(self.transactions_content)
        
        layout.addWidget(transactions_frame)
    
    def setup_advice_section(self, layout):
        """Финансовые советы"""
        advice_frame = QFrame()
        advice_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border-radius: 8px;
                border: 1px solid #90CAF9;
            }
        """)
        advice_layout = QVBoxLayout(advice_frame)
        
        advice_title = QLabel("💡 Финансовые советы")
        advice_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        advice_layout.addWidget(advice_title)
        
        self.advice_content = QLabel("Загрузка советов...")
        self.advice_content.setWordWrap(True)
        advice_layout.addWidget(self.advice_content)
        
        layout.addWidget(advice_frame)
    
    def setup_goals_section(self, layout):
        """Цели"""
        goals_frame = QFrame()
        goals_frame.setStyleSheet("""
            QFrame {
                background-color: #F3E5F5;
                border-radius: 8px;
                border: 1px solid #CE93D8;
            }
        """)
        goals_layout = QVBoxLayout(goals_frame)
        
        goals_title = QLabel("🎯 Финансовые цели")
        goals_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        goals_layout.addWidget(goals_title)
        
        self.goals_content = QLabel("Загрузка целей...")
        self.goals_content.setWordWrap(True)
        goals_layout.addWidget(self.goals_content)
        
        layout.addWidget(goals_frame)
    
    def load_data(self):
        """Загрузка данных для дашборда"""
        # Статистика за текущий месяц
        now = datetime.now()
        monthly_summary = self.transaction_ops.get_monthly_summary(
            self.user_data['id'], now.year, now.month
        )
        
        self.income_label.setText(format_currency(monthly_summary['income']))
        self.expenses_label.setText(format_currency(monthly_summary['expenses']))
        self.balance_label.setText(format_currency(monthly_summary['balance']))
        
        # Последние операции
        transactions = self.transaction_ops.get_user_transactions(self.user_data['id'])[:5]
        if transactions:
            transactions_text = ""
            for trans in transactions:
                type_icon = "⬆️" if trans['type'] == 'income' else "⬇️"
                transactions_text += f"{type_icon} {trans['category_name']}: {format_currency(trans['amount'])}\n"
            self.transactions_content.setText(transactions_text)
        else:
            self.transactions_content.setText("Операций пока нет")
        
        # Финансовые советы
        try:
            spending_advice = self.advisor.get_spending_advice()
            savings_advice = self.advisor.get_savings_advice(self.user_data.get('monthly_income', 0))
            all_advice = spending_advice + savings_advice
            
            if all_advice:
                advice_text = "\n".join([f"• {advice}" for advice in all_advice])
                self.advice_content.setText(advice_text)
            else:
                self.advice_content.setText("Пока нет персонализированных советов. Добавьте больше данных о ваших финансах.")
        except Exception as e:
            self.advice_content.setText(f"Советы временно недоступны: {str(e)}")
        
        # Цели
        goals = self.goal_ops.get_user_goals(self.user_data['id'])
        if goals:
            goals_text = ""
            for goal in goals:
                progress = (goal['current_amount'] / goal['target_amount']) * 100
                deadline_text = f" до {goal['deadline']}" if goal['deadline'] else ""
                goals_text += f"🎯 {goal['name']}: {format_currency(goal['current_amount'])} / {format_currency(goal['target_amount'])} ({progress:.1f}%){deadline_text}\n"
            self.goals_content.setText(goals_text)
        else:
            self.goals_content.setText("Цели пока не установлены. Создайте свою первую финансовую цель!")

    def refresh_data(self):
        """Обновление данных дашборда"""
        self.load_data()