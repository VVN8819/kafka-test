import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

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
        
        # =========График 1: Воронка конверсии (bar plot) ==============
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
        plt.xticks(ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # ==============График 2: Топ продуктов по выручке (horizontal bar) =================
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
            
        # ===========График 3: Активность пользователей (scatter plot)=======
        # X = user_id, Y = количество действий, размер точки = выручка
        plt.subplot(2, 3, 3)
        
        # user_id, количество действий
        user_activity = {uid: len(actions) for uid, actions in metrics.user_behavior.items()}
        
        # Считаем выручку по каждому пользователю
        user_revenue = defaultdict(float)
        for sid, data in metrics.session_data.items():
            for uid in data.get('users', set()):
                user_revenue[uid] += data.get('revenue', 0.0)
        
        if user_activity:
            user_ids = list(user_activity.keys())
            actions_count = [user_activity[uid] for uid in user_ids]
            revenue = [user_revenue.get(uid, 0) for uid in user_ids]
            
            # Размер точки пропорционален выручке
            sizes = [max(20, min(200, rev * 0.5)) for rev in revenue]
            
            scatter = plt.scatter(
                user_ids, actions_count, 
                s=sizes, 
                c=actions_count, 
                cmap='viridis', 
                alpha=0.7, 
                edgecolors='black',
                linewidth=0.5
            )
            
            # Подписи осей и заголовок
            plt.title('Активность пользователей', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('User ID', fontsize=11)
            plt.ylabel('Количество действий', fontsize=11)
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # Легенда
            plt.colorbar(scatter, label='Действий', pad=0.1)
            
            # Подпись про размер точки
            plt.text(0.5, -0.15, 'Размер точки = выручка ($)', 
                    ha='center', fontsize=9, style='italic', transform=plt.gca().transAxes)
            plt.tight_layout()
        else:
            plt.text(0.5, 0.5, 'Нет данных о пользователях', 
                    ha='center', va='center', fontsize=11, style='italic')
            plt.title('Активность пользователей', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.2)
            plt.xlabel('User ID')
            plt.ylabel('Количество действий')
            plt.tight_layout()

        # =============== График 4: Распределение длины сессий (histogram)==================
        # Гистограмма количества действий в сессии
        plt.subplot(2, 3, 4)
        
        # Количество действий в каждой сессии
        session_lengths = [
            len(data.get('actions', [])) 
            for data in metrics.session_data.values()
        ]
        
        if session_lengths:
            n, bins, patches = plt.hist(
                session_lengths, 
                bins=10,  # Количество столбцов
                color='#9b59b6',  # Фиолетовый для разнообразия
                edgecolor='black', 
                alpha=0.8,
                rwidth=0.9
            )
            
            plt.title('Распределение длины сессий', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Количество действий в сессии', fontsize=11)
            plt.ylabel('Количество сессий', fontsize=11)
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Среднее значение
            avg_length = np.mean(session_lengths)
            plt.axvline(avg_length, color='red', linestyle='--', linewidth=1.5, 
                       label=f'Среднее: {avg_length:.1f}')
            plt.legend(fontsize=9)
            plt.tight_layout()
        else:
            plt.text(0.5, 0.5, 'Нет данных о сессиях', 
                    ha='center', va='center', fontsize=11, style='italic')
            plt.title('Распределение длины сессий', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.2)
            plt.tight_layout()



        # Сохранение
        if save_path:
            save_file = self.output_dir / save_path
            plt.savefig(save_file, dpi=300, bbox_inches='tight')
            print(f"График сохранён: {save_file}")
        
        plt.show()
        
        return fig