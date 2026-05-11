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