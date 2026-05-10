import json
from kafka import KafkaConsumer
from metrics import BusinessMetrics
import numpy as np

consumer = KafkaConsumer(
    'user-actions', # ящик с письмами
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest', # Если вообще никогда не читал этот ящик, начни с самого первого письма
    group_id='demo-analytics-group' # вспомнит, на каком письме он остановился, и не заставит читать всё заново
)

metrics = BusinessMetrics()

print("Starting to consume messages...")
print("Press Ctrl+C to stop and see analytics")

message_count = 0

try:
    for message in consumer:
        event = message.value
        message_count += 1
        
        # Обработка сообщения (metrics.py)
        metrics.process_event(event, message_count)

        # Показываем статистику каждые 10 сообщений
        if message_count % 20 == 0:
            metrics.print_periodic_report(message_count)

except KeyboardInterrupt:
    print(f"\nИтого:")
    metrics.print_final_analytics(message_count)

finally:
    consumer.close()
    
