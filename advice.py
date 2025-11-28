from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.advisor import FinancialAdvisor
from utils.helpers import format_currency, show_error_message

class Advice(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.advisor = FinancialAdvisor(db_manager, user_data['id'])
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("💡 Персональные финансовые советы")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Описание
        desc = QLabel("На основе анализа ваших финансовых данных")
        desc.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(desc)
        
        # Кнопка обновления советов
        refresh_button = QPushButton("🔄 Обновить советы")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_button.clicked.connect(self.load_advice)
        layout.addWidget(refresh_button)
        
        # Область с советами
        self.advice_scroll = QScrollArea()
        self.advice_scroll.setWidgetResizable(True)
        self.advice_content = QWidget()
        self.advice_layout = QVBoxLayout(self.advice_content)
        self.advice_layout.setSpacing(15)
        self.advice_layout.setContentsMargins(10, 10, 10, 10)
        
        self.advice_scroll.setWidget(self.advice_content)
        layout.addWidget(self.advice_scroll)
        
        # Загружаем советы при инициализации
        self.load_advice()
    
    def clear_advice_layout(self):
        """Очистка компоновки от предыдущих советов"""
        # Удаляем все виджеты из компоновки
        while self.advice_layout.count():
            item = self.advice_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def load_advice(self):
        """Загрузка и отображение советов"""
        try:
            # Очищаем предыдущие советы
            self.clear_advice_layout()
            
            # Получаем советы от финансового советника
            spending_advice = self.advisor.get_spending_advice()
            savings_advice = self.advisor.get_savings_advice(self.user_data.get('monthly_income', 0))
            
            all_advice = spending_advice + savings_advice
            
            if not all_advice:
                # Если советов нет, показываем сообщение
                no_advice_label = QLabel("Пока нет персонализированных советов. Добавьте больше данных о ваших финансах.")
                no_advice_label.setWordWrap(True)
                no_advice_label.setStyleSheet("color: #666; font-size: 14px; padding: 20px;")
                no_advice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.advice_layout.addWidget(no_advice_label)
                return
            
            # Отображаем каждый совет в отдельном фрейме
            for i, advice in enumerate(all_advice):
                advice_frame = QFrame()
                advice_frame.setStyleSheet("""
                    QFrame {
                        background-color: #E3F2FD;
                        border-radius: 8px;
                        border: 1px solid #90CAF9;
                        padding: 15px;
                    }
                """)
                frame_layout = QVBoxLayout(advice_frame)
                
                # Номер совета и текст
                advice_text = QLabel(f"<b>Совет {i+1}:</b> {advice}")
                advice_text.setWordWrap(True)
                advice_text.setStyleSheet("font-size: 14px;")
                advice_text.setTextFormat(Qt.TextFormat.RichText)
                frame_layout.addWidget(advice_text)
                
                self.advice_layout.addWidget(advice_frame)
            
            # Добавляем растягивающийся элемент в конец
            self.advice_layout.addStretch()
            
        except Exception as e:
            # В случае ошибки показываем сообщение
            error_label = QLabel(f"Произошла ошибка при загрузке советов: {str(e)}")
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: #f44336; font-size: 14px; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.clear_advice_layout()
            self.advice_layout.addWidget(error_label)