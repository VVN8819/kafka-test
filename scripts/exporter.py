import pandas as pd
from pathlib import Path

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
        print(f'Экспорт завершен: {file_path}')