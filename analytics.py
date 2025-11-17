from database.operations import TransactionOperations
from datetime import datetime, timedelta

class FinancialAnalytics:
    def __init__(self, db_manager, user_id):
        self.db_manager = db_manager
        self.user_id = user_id
        self.transaction_ops = TransactionOperations(db_manager)
    
    def get_category_breakdown(self, start_date, end_date):
        """Распределение расходов по категориями"""
        transactions = self.transaction_ops.get_user_transactions(
            self.user_id, start_date, end_date
        )
        
        expenses = [t for t in transactions if t['type'] == 'expense']
        income = [t for t in transactions if t['type'] == 'income']
        
        expense_by_category = {}
        for expense in expenses:
            category = expense['category_name']
            expense_by_category[category] = expense_by_category.get(category, 0) + expense['amount']
        
        income_by_category = {}
        for inc in income:
            category = inc['category_name']
            income_by_category[category] = income_by_category.get(category, 0) + inc['amount']
        
        return {
            'expenses': expense_by_category,
            'income': income_by_category
        }
    
    def get_monthly_trends(self, months=6):
        """Тренды по месяцам"""
        end_date = datetime.now()
        trends = []
        
        for i in range(months):
            month_date = end_date - timedelta(days=30*i)
            summary = self.transaction_ops.get_monthly_summary(
                self.user_id, month_date.year, month_date.month
            )
            trends.append({
                'month': f"{month_date.year}-{month_date.month:02d}",
                'income': summary['income'],
                'expenses': summary['expenses'],
                'balance': summary['balance']
            })
        
        return list(reversed(trends))
    
    def predict_next_month(self):
        """Прогноз на следующий месяц"""
        trends = self.get_monthly_trends(3)
        if len(trends) < 2:
            return None
        
        # Простой прогноз на основе среднего
        avg_income = sum(t['income'] for t in trends) / len(trends)
        avg_expenses = sum(t['expenses'] for t in trends) / len(trends)
        
        return {
            'predicted_income': avg_income,
            'predicted_expenses': avg_expenses,
            'predicted_balance': avg_income - avg_expenses
        }