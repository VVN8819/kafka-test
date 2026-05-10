import json
from kafka import KafkaConsumer
from collections import defaultdict, Counter
import pandas as pd
from datetime import datetime
import numpy as np

consumer = KafkaConsumer(
    'user-actions', # ящик с письмами
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest', # Если вообще никогда не читал этот ящик, начни с самого первого письма
    group_id='demo-analytics-group' # вспомнит, на каком письме он остановился, и не заставит читать всё заново
)

action_stats = Counter()
product_views = Counter()
user_sessions = defaultdict(list)

# Добавлены доп метрики для отслеживания
user_behavior = defaultdict(list) # История действий по пользователям
session_data = defaultdict(dict) # Данные сессий
hourly_activity = defaultdict(int) # Активность по часам
#conversion_funnel = Counter() # Воронка конверсии
#product_performance = defaultdict(lambda: {
 #'views': 0, 'cart_adds': 0, 'purchases': 0, 'revenue': 0
#})

revenue_data = []

print("Starting to consume messages...")
print("Press Ctrl+C to stop and see analytics")

message_count = 0

try:
    for message in consumer:
        event = message.value
        message_count += 1

        # Обновляем статистику
        action_stats[event['action']] += 1

        if event.get('product'):
            product_views[event['product']] += 1

        user_sessions[event['user_id']].append(event['action'])
        
        # История действий по пользователям
        user_behavior[event['user_id']].append(event['action'])
        
        # Данные сессий
        sid = event['session_id']
        # Если списка действий в этой сессии ещё нет — создаём его
        if 'actions' not in session_data[sid]:
            session_data[sid]['actions'] = []
        session_data[sid]['actions'].append(event['action'])
        # Если множества пользователей ещё нет — создаём
        if 'users' not in session_data[sid]:
            session_data[sid]['users'] = set()
        session_data[sid]['users'].add(event['user_id'])
        
        # Активность по часам
        event_hour = datetime.fromisoformat(event['timestamp']).hour # номер часа из ISO-строки
        hourly_activity[event_hour] += 1

        if event.get('price'):
            revenue_data.append(event['price'])

        print(f"Message {message_count}: {event['action']} - {event.get('product', 'N/A')} - User {event['user_id']}")

        # Показываем статистику каждые 10 сообщений
        if message_count % 10 == 0:
            print(f"\n--- Stats after {message_count} messages ---")
            print("Top actions:")
            for action, count in action_stats.most_common(3):
                print(f"  {action}: {count}")
            print(f"Active users: {len(user_sessions)}")
            print("-" * 50)

except KeyboardInterrupt:
    print(f"\nStopped after {message_count} messages")
    
    # Анализ "История действий по пользователям"
    if user_behavior:
        # Словарь в список для DataFrame
        user_behav_data = [(uid, act) for uid, acts in user_behavior.items() for act in acts]
        df = pd.DataFrame(user_behav_data, columns=['user_id', 'action'])

        # список - 5 частых посетителей
        top_users = df.groupby('user_id').size().sort_values(ascending=False).head(5)
        print(f'5 частых посетителей: {top_users}')

    else:
        print(f'\nИстория действий по пользователям не собрана!')
        
    # Анализ сессий
    if session_data:
        print(f'\nУникальных сессий: {len(session_data)}')
    else:
        print('\nДанные сессий не собраны!')
        
    # Анализ активности по часам
    if hourly_activity:
        for hour in sorted(hourly_activity.keys()):
            print(f'{hour:02d}:00 - {hourly_activity[hour]} сообщений')
    else:
        print('Нет данных активность по часам.')
