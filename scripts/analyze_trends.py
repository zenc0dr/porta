#!/usr/bin/env python3
import json
import os
import glob
from datetime import datetime, timedelta
import statistics

def load_metrics():
    """Загружает все метрики из папки logs/daily_metrics"""
    metrics = []
    pattern = "logs/daily_metrics/*.json"
    
    for filename in glob.glob(pattern):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                # Извлекаем дату из имени файла
                date_str = os.path.basename(filename).replace('.json', '')
                data['date'] = date_str
                metrics.append(data)
        except Exception as e:
            print(f"⚠️  Ошибка чтения {filename}: {e}")
    
    # Сортируем по дате
    metrics.sort(key=lambda x: x['date'])
    return metrics

def analyze_trends(metrics):
    """Анализирует тренды производительности"""
    if len(metrics) < 2:
        print("📊 Недостаточно данных для анализа трендов (нужно минимум 2 дня)")
        return
    
    print("📈 Анализ трендов производительности")
    print("=" * 50)
    
    # Последние 7 дней
    recent = metrics[-7:] if len(metrics) >= 7 else metrics
    
    # Средние значения
    avg_cv = statistics.mean([m.get('cv_latency', 0) for m in recent])
    avg_p95 = statistics.mean([m.get('p95_latency_ms', 0) for m in recent])
    avg_p99 = statistics.mean([m.get('p99_latency_ms', 0) for m in recent])
    
    print(f"📊 Средние значения за {len(recent)} дней:")
    print(f"   CV: {avg_cv:.1f}%")
    print(f"   P95: {avg_p95:.1f}ms")
    print(f"   P99: {avg_p99:.1f}ms")
    
    # Тренды
    if len(metrics) >= 3:
        first_week = metrics[:3]
        last_week = metrics[-3:]
        
        first_avg_cv = statistics.mean([m.get('cv_latency', 0) for m in first_week])
        last_avg_cv = statistics.mean([m.get('cv_latency', 0) for m in last_week])
        
        cv_trend = "📈" if last_avg_cv > first_avg_cv else "📉"
        print(f"\n{cv_trend} Тренд CV: {first_avg_cv:.1f}% → {last_avg_cv:.1f}%")
    
    # Рекомендации
    print("\n💡 Рекомендации:")
    if avg_cv > 50:
        print("   ⚠️  Высокая нестабильность (CV > 50%)")
        print("   🔍 Проверьте нагрузку на систему")
    elif avg_cv > 30:
        print("   ⚠️  Умеренная нестабильность (CV > 30%)")
        print("   📊 Продолжайте мониторинг")
    else:
        print("   ✅ Стабильная производительность")
    
    if avg_p95 > 2000:
        print("   ⚠️  Высокие задержки (P95 > 2000ms)")
        print("   🔧 Рассмотрите оптимизацию")
    elif avg_p95 > 1000:
        print("   ⚠️  Умеренные задержки (P95 > 1000ms)")
        print("   📊 Требует внимания")

def main():
    print("🔍 Анализ трендов Porta")
    print("=" * 30)
    
    metrics = load_metrics()
    
    if not metrics:
        print("❌ Нет данных для анализа")
        print("💡 Запустите: python3 scripts/run_diagnostics.py")
        return
    
    print(f"📁 Найдено {len(metrics)} отчётов")
    
    # Показываем последние метрики
    latest = metrics[-1]
    print(f"\n📊 Последний отчёт ({latest['date']}):")
    print(f"   CV: {latest.get('cv_latency', 'N/A')}%")
    print(f"   P95: {latest.get('p95_latency_ms', 'N/A')}ms")
    print(f"   P99: {latest.get('p99_latency_ms', 'N/A')}ms")
    print(f"   Успешных: {latest.get('successful', 'N/A')}")
    print(f"   Ошибок: {latest.get('errors', 'N/A')}")
    
    analyze_trends(metrics)

if __name__ == "__main__":
    main() 