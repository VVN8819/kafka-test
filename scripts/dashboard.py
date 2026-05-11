import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

class Dashboard:
    def __init__(self, output_dir="data"):
        self.output_dir=Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_dashboard(self, metrics, save_path="kafka_analytics_dashboard.png"):
        fig = plt.figure(figsize=(16, 12))
        
        # ========= Воронка конверсии (bar plot) ==============
        # Покажите: просмотры → корзина → покупки
        plt.subplot(2, 3, 1)
        
        funnel_data = {
            "View": metrics.conversion_funnel.get('view_product', 0),
            "Cart": metrics.conversion_funnel.get('add_to_cart', 0),
            "Purchases": metrics.conversion_funnel.get('purchase', 0),
        }
        
        keys = list(funnel_data.keys())
        values = list(funnel_data.values())
        colors = ['red', 'green', 'grey']
        
        # bar plot
        bars = plt.bar(keys, values, color=colors, edgecolor='black', alpha=0.7)
        
        # Подписи значений на столбцы
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02, 
                    f'{val}', ha='center', va='bottom', fontweight='bold')
        
        # Оформление
        plt.title('Воронка конверсии', fontsize=14, fontweight='bold')
        plt.ylabel('Количество событий')
        plt.xlabel('Этап воронки')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Сохранение
        if save_path:
            save_file = self.output_dir / save_path
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            print(f"График сохранён: {save_file}")
        
        plt.show()
        
        return fig