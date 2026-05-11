import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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
        
        # ============== Топ продуктов по выручке (horizontal bar) =================
        # Покажите выручку по каждому продукту
        plt.subplot(2, 3, 2)
        
        product_revenue = {
            product: data['revenue'] 
            for product, data in metrics.product_performance.items()
        }
        
        # Сортируем по выручке и берём топ-5
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if sorted_products:
            products, revenues = zip(*sorted_products)
            
            # Генерация цветов
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(products)))
            bars = plt.barh(products, revenues, color=colors, edgecolor='black', alpha=0.9)
            
            # Подписи значений на барах
            for bar, rev in zip(bars, revenues):
                plt.text(bar.get_width() + rev*0.01, bar.get_y() + bar.get_height()/2, 
                        f'${rev:.0f}', va='center', fontsize=9, fontweight='bold')
                
            plt.title('Топ продуктов по выручке', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Выручка', fontsize=11)
            plt.ylabel('Продукт', fontsize=11)
            plt.grid(axis='x', alpha=0.3, linestyle='--')  # Сетка по горизонтали
            plt.gca().invert_yaxis()  # Чтобы топ-1 был сверху
            plt.tight_layout()
        else:
            plt.text(0.5, 0.5, 'Нет данных о продуктах', 
                    ha='center', va='center', fontsize=11, style='italic')
            plt.title('Топ продуктов по выручке', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.2)
            plt.tight_layout()

        # Сохранение
        if save_path:
            save_file = self.output_dir / save_path
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            print(f"График сохранён: {save_file}")
        
        plt.show()
        
        return fig