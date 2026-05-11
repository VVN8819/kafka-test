import json
from kafka import KafkaConsumer
from metrics import BusinessMetrics
from alert import AlertManager
from exporter import DataExporter
import numpy as np

consumer = KafkaConsumer(
    'user-actions', # ящик с письмами
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest', # Если вообще никогда не читал этот ящик, начни с самого первого письма
    group_id='demo-analytics-group' # вспомнит, на каком письме он остановился, и не заставит читать всё заново
)

metrics = BusinessMetrics()
alerts = AlertManager()
exporter = DataExporter()

print("Starting to consume messages...")
print("Press Ctrl+C to stop and see analytics")

message_count = 0

#  Проверить на подозрительную активность и бизнес-проблемы
recent_events = [] 
ses_size = 20  # последние 20 сообщений

try:
    for message in consumer:
        event = message.value
        message_count += 1
        
        # Обработка сообщения (metrics.py)
        metrics.process_event(event, message_count)
        
        #  Проверить на подозрительную активность и бизнес-проблемы
        recent_events.append(event)
        if len(recent_events) > ses_size:
            recent_events.pop(0)

        # Показываем статистику каждые 20 сообщений
        if message_count % 20 == 0:
            metrics.print_periodic_report(message_count)
            
            alerts.check_logout_rate(recent_events)
            alerts.check_abandonment_rate(recent_events)
            alerts.check_user_activity(recent_events)
            alerts.check_no_purchases(recent_events)

except KeyboardInterrupt:
    print(f"\nИтого:")
    metrics.print_final_analytics(message_count)
    exporter.export_session_data_to_csv(metrics.session_data)

finally:
    consumer.close()
    
