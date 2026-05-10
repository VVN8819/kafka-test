from collections import defaultdict, Counter
import pandas as pd
from datetime import datetime

class BusinessMetrics:
    def __init__(self):
        self.action_stats = Counter()
        self.product_views = Counter()
        self.user_sessions = defaultdict(list)

        # Добавлены доп метрики для отслеживания
        self.user_behavior = defaultdict(list) # История действий по пользователям
        self.session_data = defaultdict(dict) # Данные сессий
        self.hourly_activity = defaultdict(int) # Активность по часам
        self.conversion_funnel = Counter() # Воронка конверсии
        self.product_performance = defaultdict(lambda: {
                'views': 0,
                'cart_adds': 0,
                'purchases': 0,
                'revenue': 0
            })

        self.revenue_data = []
        
    def process_event(self, event, message_count):
        action = event['action']
        
        # Обновляем статистику
        self.action_stats[action] += 1

        if event.get('product'):
            self.product_views[event['product']] += 1
        
        user_id = event['user_id']
        self.user_sessions[user_id].append(action)
        # История действий по пользователям
        self.user_behavior[user_id].append(action)
        
        # Данные сессий, Средний чек сессии
        sid = event['session_id']
        # Если списка действий в этой сессии ещё нет — создаём его
        if sid not in self.session_data:
            self.session_data[sid] = {'actions': [], 'users': set(), 'revenue': 0.0}
        self.session_data[sid]['actions'].append(action)
        self.session_data[sid]['users'].add(user_id)
        
        # Активность по часам
        event_hour = datetime.fromisoformat(event['timestamp']).hour # номер часа из ISO-строки
        self.hourly_activity[event_hour] += 1

        if event.get('price'):
            self.revenue_data.append(event['price'])
            self.session_data[sid]['revenue'] += event['price'] # Средний чек сессии
            
        # Воронка конверсии
        if action in ['view_product', 'add_to_cart', 'purchase', 'search']:
            self.conversion_funnel[action] += 1
            
        # Эффективность продукта
        product = event.get('product')
        if product:
            if action == 'view_product':
                self.product_performance[product]['views'] += 1
            elif action == 'add_to_cart':
                self.product_performance[product]['cart_adds'] += 1
            elif action == 'purchase':
                self.product_performance[product]['purchases'] += 1
                price = event.get('price')
                if price:
                    self.product_performance[product]['revenue'] += price
        
        print(f"Message {message_count}: {event['action']} - {event.get('product', 'N/A')} - User {event['user_id']} - {event.get('price', 'N/A')}")
    
    # Рассчитать конверсии                
    def calculate_conversion_rates(self):
        # Анализ Воронка конверсии
        search = self.conversion_funnel['search']
        views = self.conversion_funnel['view_product']
        cart = self.conversion_funnel['add_to_cart']
        purchases = self.conversion_funnel['purchase']

        # Процент конверсии
        to_views_pct = (views / search) * 100 if cart > 0 else 0
        to_cart_pct = (cart / views) * 100 if cart > 0 else 0
        to_buy_pct = (purchases / cart) * 100 if cart > 0 else 0
        
        return{
            'search': search,
            'views': views,
            'cart_adds': cart,
            'purchases': purchases,
            'to_views_pct': round(to_views_pct, 2),
            'to_cart_pct': round(to_cart_pct, 2),
            'to_buy_pct': round(to_buy_pct, 2)
        }
    
    # Средний чек сессии
    def calculate_average_session_value(self) -> float:
        if not self.session_data:
            return 0.0
        # Суммируем выручку всех сессий и делим на их количество
        total_revenue = sum(session.get('revenue', 0.0) for session in self.session_data.values())
        avg_value = total_revenue / len(self.session_data)
        
        return round(avg_value, 2)
    
    # Анализ "История действий по пользователям" Топ-5 самых активных пользователей
    def find_top_customers(self):
        if not self.user_behavior:
            return []
    
        # Словарь в список для DataFrame
        user_behav_data = [(uid, act) for uid, acts in self.user_behavior.items() for act in acts]
        df = pd.DataFrame(user_behav_data, columns=['user_id', 'action'])
        # список - 5 частых посетителей
        top_users = df.groupby('user_id').size().sort_values(ascending=False).head(5)
        return [{"user_id": uid, "actions_count": int(count)} for uid, count in top_users.items()]
    
        
    def print_periodic_report(self, message_count):
        rates = self.calculate_conversion_rates() # Рассчитать конверсии
        avg_session_val = self.calculate_average_session_value() #Средний чек сессии
        top_customers = self.find_top_customers() # Топ-5 самых активных пользователей
        # Показываем статистику каждые 20 сообщений
        
        print(f"\n--- Stats after {message_count} messages ---")
        print("Top actions:")
        for action, count in self.action_stats.most_common(3):
            print(f"  {action}: {count}")
        print(f"Active users: {len(self.user_sessions)}")
        print("-" * 50)
        # Отображение Воронка конверсии
        print('\nВоронка конверсии:')
        print(f'Поиск: {rates['search']}')
        print(f'Просмотры: {rates['views']}')
        print(f'Корзина: {rates['cart_adds']}')
        print(f'Покупки: {rates['purchases']}')
        print(f'Конверсия Поиск в Просмотр: {rates['to_views_pct']}%')
        print(f'Конверсия Просмотр в Корзина: {rates['to_cart_pct']}%')
        print(f'Конверсия Корзина в Покупка: {rates['to_buy_pct']}%')
        print("-" * 50)
        print(f'\nСредний чек сессий: {avg_session_val}')
        print("-" * 50)
        print('\nТоп-5 самых активных пользователей:')
        if top_customers:
            for rank, cust in enumerate(top_customers, 1):
                print(f'#{rank} | User: {cust['user_id']} | Actions: {cust['actions_count']}')
        else:
            print('Нет данных!')
        
        
    def print_final_analytics(self, message_count):
        print(f"\nStopped after {message_count} messages")
        print("-" * 50)
        
        # Анализ "История действий по пользователям"
        top_customers = self.find_top_customers() # Топ-5 самых активных пользователей
        print('\nТоп-5 самых активных пользователей:')
        if top_customers:
            for rank, cust in enumerate(top_customers, 1):
                print(f'#{rank} | User: {cust['user_id']} | Actions: {cust['actions_count']}')
        else:
            print('Нет данных!')
            
        # Анализ сессий
        avg_session_val = self.calculate_average_session_value() #Средний чек сессии
        print(f'\nУникальных сессий: {len(self.session_data)}')
        print(f'\nСредний чек сессий: {avg_session_val}')
        
        # Анализ активности по часам
        for hour in sorted(self.hourly_activity.keys()):
            print(f'{hour:02d}:00 - {self.hourly_activity[hour]} сообщений')
        
        # Отображение Воронка конверсии
        rates = self.calculate_conversion_rates()
        print('\nВоронка конверсии:')
        print(f'Поиск: {rates['search']} шт.')
        print(f'Просмотры: {rates['views']} шт.')
        print(f'Корзина: {rates['cart_adds']} шт.')
        print(f'Покупки: {rates['purchases']} шт.')
        print(f'Конверсия Поиск в Просмотр: {rates['to_views_pct']}%')
        print(f'Конверсия Просмотр в Корзина: {rates['to_cart_pct']}%')
        print(f'Конверсия Корзина в Покупка: {rates['to_buy_pct']}%')
        
        # Анализ Эффективность продукта
        if self.product_performance:
            df_products = pd.DataFrame(self.product_performance).T
            # Сортируем по выручке для наглядности
            df_products = df_products.sort_values(by='revenue', ascending=False)
            print(f'\nТаблица Эффективность продукта: \n{df_products}')

            