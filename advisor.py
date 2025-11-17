from database.operations import TransactionOperations
from datetime import datetime, timedelta

class FinancialAdvisor:
    def __init__(self, db_manager, user_id):
        self.db_manager = db_manager
        self.user_id = user_id
        self.transaction_ops = TransactionOperations(db_manager)
    
    def get_spending_advice(self):
        """Получение советов по расходам"""
        advice = []
        
        try:
            # Анализ расходов за последний месяц
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            transactions = self.transaction_ops.get_user_transactions(
                self.user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            )
            
            expenses = [t for t in transactions if t['type'] == 'expense']
            if not expenses:
                return ["У вас не было расходов за последний месяц. Отлично!"]
            
            total_expenses = sum(e['amount'] for e in expenses)
            category_totals = {}
            for expense in expenses:
                category = expense['category_name']
                category_totals[category] = category_totals.get(category, 0) + expense['amount']
            
            # Совет по самой затратной категории
            if category_totals:
                max_category = max(category_totals, key=category_totals.get)
                max_amount = category_totals[max_category]
                percentage = (max_amount / total_expenses) * 100
                
                if percentage > 50:
                    advice.append(f"Вы тратите {percentage:.1f}% бюджета на {max_category}. Возможно, стоит сократить эти расходы.")
            
            # Сравнение с предыдущим месяцем
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=30)
            prev_transactions = self.transaction_ops.get_user_transactions(
                self.user_id, prev_start_date.strftime('%Y-%m-%d'), prev_end_date.strftime('%Y-%m-%d')
            )
            prev_expenses = sum(t['amount'] for t in prev_transactions if t['type'] == 'expense')
            
            if prev_expenses > 0:
                change = ((total_expenses - prev_expenses) / prev_expenses) * 100
                if change > 20:
                    advice.append(f"Ваши расходы выросли на {change:.1f}% по сравнению с предыдущим месяцем.")
                elif change < -20:
                    advice.append(f"Ваши расходы уменьшились на {abs(change):.1f}% по сравнению с предыдущим месяцем. Отлично!")
            
            if not advice:
                advice.append("Ваши расходы выглядят стабильно. Продолжайте в том же духе!")
        
        except Exception as e:
            advice = [f"Не удалось проанализировать расходы. Добавьте больше данных о ваших операциях."]
        
        return advice
    
    def get_savings_advice(self, monthly_income):
        """Советы по накоплениям"""
        if monthly_income <= 0:
            return ["Укажите ваш месячный доход в настройках для получения советов по накоплениям"]
        
        try:
            transactions = self.transaction_ops.get_user_transactions(self.user_id)
            total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
            total_savings = total_income - total_expenses
            
            savings_rate = (total_savings / monthly_income) * 100 if monthly_income > 0 else 0
            
            advice = []
            if savings_rate < 10:
                advice.append(f"Рекомендуется откладывать не менее 10% от дохода. Сейчас у вас {savings_rate:.1f}%")
            elif savings_rate > 20:
                advice.append(f"Отличная норма сбережений! {savings_rate:.1f}% - это выше среднего")
            else:
                advice.append(f"Норма сбережений {savings_rate:.1f}% в пределах рекомендаций")
            
            return advice
        except Exception as e:
            return [f"Не удалось проанализировать накопления. Добавьте данные о доходах и расходах."]