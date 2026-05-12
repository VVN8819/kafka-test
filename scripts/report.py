from datetime import timedelta
class ReportGenerator:
    
    def print_executive_summary(self, metrics, message_count, duration: timedelta):
        """
        Напечатать executive summary для руководства
        """
        # Время работы в минутах
        total_seconds = duration.total_seconds()
        minutes = int(total_seconds // 60)
        
        # Производительность (событий/сек)
        efficiency = message_count / total_seconds if total_seconds > 0 else 0
        
        # Уникальных пользователей
        unique_users = len(metrics.user_sessions)

        # Конверсия
        funnel = metrics.conversion_funnel
        views = funnel.get('view_product', 0)
        purchases = funnel.get('purchase', 0)
        conversion_rate = (purchases / views * 100) if views > 0 else 0.0

        # Выручка и Топ-продукт
        total_revenue = 0.0
        top_product_name = "N/A"
        top_product_rev = 0.0

        if metrics.product_performance:
            # Топ продукт
            top_product_name, data = max(metrics.product_performance.items(), key=lambda x: x[1]['revenue'])
            top_product_rev = data['revenue']
            
            # Общая выручка
            total_revenue = sum(item['revenue'] for item in metrics.product_performance.values())

        # Алерты
        abandoned_count = len(metrics.detect_abandoned_sessions())
        
        # 2. Красивый текстовый отчет
        print("\n" + "=" * 45)
        print("📊 REAL-TIME ANALYTICS REPORT")
        print("=" * 45)
        print(f"\n📈 Обработано событий: {message_count}")
        print(f"\n👥 Уникальных пользователей: {unique_users}")
        print(f"\n🛒 Конверсия в покупку: {conversion_rate:.1f}%")
        print(f"\n💰 Общая выручка: ${total_revenue:,.0f}")
        print(f"\n⭐ Топ продукт: {top_product_name} (${top_product_rev:,.0f})")
        print(f"\n⚠️ Алерты: {abandoned_count} подозрительных сессий")
        print("=" * 45)
        print("⚙️ Производительность")
        print("=" * 45)
        print(f"⏱️  Время работы системы: {minutes} мин")
        print(f"🚀 Производительность: {efficiency:.2f} событий/сек")
        print("=" * 45 + "\n")