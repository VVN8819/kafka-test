class AlertManager:
    
    def check_for_alerts(self, recent_events):
        """
         Проверить на подозрительную активность и бизнес-проблемы

         Алерты:
         1. Слишком много logout'ов (>50% от всех действий)
         2. Высокий уровень отказов от корзины (cart без purchase)
         3. Один пользователь делает >10 действий за минуту
         4. Нет покупок в последних 50 событиях
         """
        print(f'\nПроверка на подозрительную активность и бизнес-проблемы ЗАПУЩЕНА!')
        
        if not recent_events:
            return

        total_actions = len(recent_events)
        
        # Считаем logout
        logout_count = sum(1 for event in recent_events if event.get('action') == 'logout')
        
        if total_actions > 0:
            logout_percentage = (logout_count / total_actions) * 100
            
            if logout_percentage > 50:
                print("-" * 50)
                print(f'\nВысокий % logout: {logout_percentage:.1f}%')