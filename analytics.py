from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QMargins
from PyQt6.QtGui import QFont, QPainter, QColor
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from database.operations import TransactionOperations
from core.analytics import FinancialAnalytics
from utils.helpers import format_currency
from datetime import datetime, timedelta

class Analytics(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.transaction_ops = TransactionOperations(db_manager)
        self.analytics = FinancialAnalytics(db_manager, user_data['id'])
        self.initUI()
        self.load_data()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("📈 Аналитика финансов")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Период для анализа
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Период анализа:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Последние 30 дней", "Последние 3 месяца", "Текущий год", "За всё время"])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        period_layout.addWidget(self.period_combo)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Прокручиваемая область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(20)
        
        # Место для графиков
        self.setup_charts_area()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def setup_charts_area(self):
        """Настройка области с графиками"""
        # График распределения расходов по категориям
        expenses_frame = QFrame()
        expenses_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        expenses_layout = QVBoxLayout(expenses_frame)
        
        expenses_title = QLabel("📊 Распределение расходов по категориям")
        expenses_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        expenses_layout.addWidget(expenses_title)
        
        self.expenses_chart_view = QChartView()
        self.expenses_chart_view.setMinimumHeight(400)
        self.expenses_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        expenses_layout.addWidget(self.expenses_chart_view)
        
        self.scroll_layout.addWidget(expenses_frame)
        
        # График доходов и расходов по месяцам
        trends_frame = QFrame()
        trends_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        trends_layout = QVBoxLayout(trends_frame)
        
        trends_title = QLabel("📈 Динамика доходов и расходов")
        trends_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        trends_layout.addWidget(trends_title)
        
        self.trends_chart_view = QChartView()
        self.trends_chart_view.setMinimumHeight(400)
        self.trends_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        trends_layout.addWidget(self.trends_chart_view)
        
        self.scroll_layout.addWidget(trends_frame)
        
        # Статистика
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📋 Финансовая статистика")
        stats_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_layout.addWidget(stats_title)
        
        self.stats_content = QLabel("Загрузка статистики...")
        self.stats_content.setWordWrap(True)
        self.stats_content.setTextFormat(Qt.TextFormat.RichText)
        stats_layout.addWidget(self.stats_content)
        
        self.scroll_layout.addWidget(stats_frame)
    
    def load_data(self):
        """Загрузка данных для аналитики"""
        self.update_expenses_chart()
        self.update_trends_chart()
        self.update_stats()
    
    def on_period_changed(self):
        """Обновление графиков при изменении периода"""
        self.load_data()
    
    def update_expenses_chart(self):
        """Обновление круговой диаграммы расходов"""
        try:
            # Получаем данные за выбранный период
            end_date = datetime.now()
            start_date = self.get_start_date()
            
            breakdown = self.analytics.get_category_breakdown(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            # Создаем серию для круговой диаграммы
            series = QPieSeries()
            series.setHoleSize(0.3)  # Делаем диаграмму кольцевой
            
            expenses = breakdown['expenses']
            total_expenses = sum(expenses.values())
            
            if total_expenses == 0:
                # Если нет расходов, показываем сообщение
                chart = QChart()
                chart.setTitle("Нет данных о расходах за выбранный период")
                self.expenses_chart_view.setChart(chart)
                return
            
            # Цвета для категорий как QColor объекты
            colors = [
                QColor('#FF6384'), QColor('#36A2EB'), QColor('#FFCE56'), 
                QColor('#4BC0C0'), QColor('#9966FF'), QColor('#FF9F40'), 
                QColor('#FF6384'), QColor('#C9CBCF')
            ]
            
            for i, (category, amount) in enumerate(expenses.items()):
                if amount > 0:
                    percentage = (amount / total_expenses) * 100
                    slice_ = series.append(f"{category} ({percentage:.1f}%)", amount)
                    slice_.setColor(colors[i % len(colors)])
            
            # Создаем chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Распределение расходов по категориям")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
            chart.setMargins(QMargins(10, 10, 10, 10))
            
            self.expenses_chart_view.setChart(chart)
            
        except Exception as e:
            # В случае ошибки показываем пустой график с сообщением
            chart = QChart()
            chart.setTitle(f"Ошибка при построении графика: {str(e)}")
            self.expenses_chart_view.setChart(chart)
    
    def update_trends_chart(self):
        """Обновление графика трендов доходов и расходов"""
        try:
            trends = self.analytics.get_monthly_trends(6)  # Последние 6 месяцев
            
            if len(trends) < 2:
                # Если недостаточно данных, показываем сообщение
                chart = QChart()
                chart.setTitle("Недостаточно данных для построения графика")
                self.trends_chart_view.setChart(chart)
                return
            
            # Создаем наборы данных для столбчатой диаграммы
            income_set = QBarSet("Доходы")
            income_set.setColor(QColor("#4CAF50"))
            
            expenses_set = QBarSet("Расходы")
            expenses_set.setColor(QColor("#F44336"))
            
            categories = []
            for trend in trends:
                # Форматируем месяц для отображения
                year_month = trend['month'].split('-')
                if len(year_month) == 2:
                    month_name = self.get_month_name(int(year_month[1]))
                    categories.append(f"{month_name} {year_month[0]}")
                else:
                    categories.append(trend['month'])
                    
                income_set.append(trend['income'])
                expenses_set.append(trend['expenses'])
            
            series = QBarSeries()
            series.append(income_set)
            series.append(expenses_set)
            
            # Создаем chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Динамика доходов и расходов по месяцам")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            
            # Ось категорий (месяцы)
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)
            
            # Ось значений
            axis_y = QValueAxis()
            axis_y.setLabelFormat("₽ %.0f")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
            chart.setMargins(QMargins(10, 10, 10, 10))
            
            self.trends_chart_view.setChart(chart)
            
        except Exception as e:
            chart = QChart()
            chart.setTitle(f"Ошибка при построении графика: {str(e)}")
            self.trends_chart_view.setChart(chart)
    
    def get_month_name(self, month_num):
        """Получение названия месяца по номеру"""
        months = [
            "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
            "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else f"М{month_num}"
    
    def update_stats(self):
        """Обновление статистики"""
        try:
            end_date = datetime.now()
            start_date = self.get_start_date()
            
            breakdown = self.analytics.get_category_breakdown(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            total_income = sum(breakdown['income'].values())
            total_expenses = sum(breakdown['expenses'].values())
            balance = total_income - total_expenses
            
            stats_text = f"""
            <b>Общая статистика за период:</b><br>
            • Доходы: <span style='color: #4CAF50;'>{format_currency(total_income)}</span><br>
            • Расходы: <span style='color: #F44336;'>{format_currency(total_expenses)}</span><br>
            • Баланс: <span style='color: {'#4CAF50' if balance >= 0 else '#F44336'};'>{format_currency(balance)}</span><br><br>
            """
            
            # Находим самые крупные категории расходов
            top_expenses = sorted(breakdown['expenses'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            if top_expenses and total_expenses > 0:
                stats_text += "<b>Самые крупные категории расходов:</b><br>"
                for category, amount in top_expenses:
                    percentage = (amount / total_expenses * 100)
                    stats_text += f"• {category}: {format_currency(amount)} ({percentage:.1f}%)<br>"
            
            # Прогноз на следующий месяц
            prediction = self.analytics.predict_next_month()
            if prediction:
                stats_text += f"<br><b>Прогноз на следующий месяц:</b><br>"
                stats_text += f"• Доходы: ~{format_currency(prediction['predicted_income'])}<br>"
                stats_text += f"• Расходы: ~{format_currency(prediction['predicted_expenses'])}<br>"
                stats_text += f"• Баланс: ~{format_currency(prediction['predicted_balance'])}"
            
            self.stats_content.setText(stats_text)
            
        except Exception as e:
            self.stats_content.setText(f"Ошибка при загрузке статистики: {str(e)}")
    
    def get_start_date(self):
        """Получение даты начала периода в зависимости от выбора"""
        period = self.period_combo.currentText()
        end_date = datetime.now()
        
        if period == "Последние 30 дней":
            return end_date - timedelta(days=30)
        elif period == "Последние 3 месяца":
            return end_date - timedelta(days=90)
        elif period == "Текущий год":
            return datetime(end_date.year, 1, 1)
        else:  # За всё время
            # Возвращаем очень раннюю дату
            return datetime(2000, 1, 1)