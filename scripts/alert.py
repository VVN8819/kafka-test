from collections import Counter
from datetime import datetime, timedelta

class AlertManager:
    
    def __init__(self):
        self.default_logout_rate = 50
        self.default_abandonment_rate = 6
    
    def check_logout_rate(self, recent_events):
        """
         Проверить на подозрительную активность и бизнес-проблемы

         Алерты:
         1. Слишком много logout'ов (>50% от всех действий)
         """
        print(f'\nПроверка на подозрительный logout ЗАПУЩЕНА!')
        
        if not recent_events:
            return

        total_actions = len(recent_events)
        
        # Считаем logout
        logout_count = sum(1 for event in recent_events if event.get('action') == 'logout')
        
        if total_actions > 0:
            logout_percentage = (logout_count / total_actions) * 100
            
            if logout_percentage > self.default_logout_rate:
                print("-" * 50)
                print(f'\nВысокий % logout: {logout_percentage:.1f}%')
                print("-" * 50)
                
    def check_abandonment_rate(self, recent_events):
        """
         Проверить на подозрительную активность и бизнес-проблемы

         Алерты:
         2. Высокий уровень отказов от корзины (cart без purchase)
         """
        print(f'Проверка на Высокий уровень отказов от корзины ЗАПУЩЕНА!')
        
        if not recent_events:
            return
        
        # Считаем действия
        cart_adds = sum(1 for event in recent_events if event.get('action') == 'add_to_cart')
        purchases = sum(1 for event in recent_events if event.get('action') == 'purchase')
        
        if cart_adds == 0:
            return
        
        abandonment_rate = ((cart_adds - purchases) / cart_adds) * 100
        
        if abandonment_rate > self.default_abandonment_rate:
            print("-" * 50)
            print(f'\nВысокий уровень отказов от корзины: {abandonment_rate:.1f}%')
            print("-" * 50)
            
    def check_user_activity(self, recent_events):
        """
        Проверить на подозрительную активность и бизнес-проблемы

         Алерты:
         3. Один пользователь делает >10 действий за минуту
        """
        print(f'Проверка на спам ЗАПУЩЕНА!')
        
        if not recent_events:
            return
        
        # Определяем окно 1 мин
        now = datetime.now()
        min_ago = now - timedelta(minutes=1)
        
        user_counts = Counter()
        
        for event in recent_events:
            # Получаем время события
            event_time = datetime.fromisoformat(event['timestamp'])
            
            if event_time > min_ago:
                user_counts[event['user_id']] += 1
        
        # 3. Проверяем > 10
        if user_counts:
            top_user, count = user_counts.most_common(1)[0]
            
            if count > 10:
                print("-" * 50)
                print(f'\nОдин пользователь делает >10 действий за минуту')
                print(f'Пользователь {top_user} делает {count} действий за минуту')
                print("-" * 50)
                
    def check_no_purchases(self, recent_events):
        """
        Проверить на подозрительную активность и бизнес-проблемы

         Алерты:
         4. Нет покупок в последних 50 событиях
        """
        print(f'Проверка на отсутствие покупок ЗАПУЩЕНА!')
        
        if len(recent_events) < 40:
            return
        
        # any() возвращает True, если условие выполнилось хоть раз
        has_purchase = any(event.get('action') == 'purchase' for event in recent_events)
        
        if not has_purchase:
            print("-" * 50)
            print(f'\nНет покупок в последних {len(recent_events)} событиях')
            print("-" * 50)