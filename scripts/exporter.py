import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class DataExporter:
    def __init__(self, output_dir="data"):
        # Создаём папку data, если её нет
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_session_data_to_csv(self, session_data, filename="user_sessions.csv"):
        """Сохранить данные о сессиях в CSV для дальнейшего анализа
        Создайте DataFrame с данными сессий и сохраните в user_sessions.csv"""
        if not session_data:
            print('Нет данных сессий для экспорта.')
            return
        
        rows_list = []
        for sid, data in session_data.items():
            rows_list.append({
                "session_id": 'sid',
                "user_id": list(data.get('users', set())),
                "actions": data.get('actions', []),
                "actions_count": len(data.get('actions', [])),
                "revenue": data.get('revenue', 0.0)
            })
            
        df = pd.DataFrame(rows_list)
        
        # Сохраняем в CSV
        file_path = self.output_dir / filename
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f'Экспорт данных о сессиях завершен: {file_path}')
        
    def save_real_time_metrics(self, metrics, message_count=0, filename="metrics_snapshot.json"):
        """Сохранить текущие метрики в JSON файл
        Сохраните все рассчитанные метрики в metrics_snapshot.json"""
        
        snapshot = {
            "snapshot_timestamp": datetime.now().isoformat(),
            "message_count": message_count,
            "conversion_funnel": dict(metrics.conversion_funnel),
            "conversion_rates": metrics.calculate_conversion_rates(),
            "revenue": {
                "total_revenue": sum(metrics.revenue_data),
                "revenue_trans_count": len(metrics.revenue_data),
                "average_session_value": metrics.calculate_average_session_value()
            },
            "hourly_activity": {str(h): v for h, v in sorted(metrics.hourly_activity.items())},
            "top_customers": metrics.find_top_customers(),
            "abandoned_sessions": len(metrics.detect_abandoned_sessions()),
            "unique_session": len(metrics.session_data),
            "unique_users": len(metrics.user_sessions),
        }
        
        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
            
        print(f'Текущая метрика экспортирована в: {file_path}')