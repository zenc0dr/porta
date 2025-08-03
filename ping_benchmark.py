#!/usr/bin/env python3
"""
Скрипт для измерения стабильности отклика Porta
Проводит серию быстрых запросов для оценки latency
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime

# Конфигурация
BASE_URL = "http://localhost:8111"
TOKEN = "test123"
AGENT_ID = "ping-test-agent"

# Простые endpoints для быстрого тестирования
QUICK_ENDPOINTS = [
    ("GET", "/meta"),
    ("GET", "/public_url"),
    ("POST", "/agent/status"),
]

POST_DATA = {
    "/agent/status": {"agent_id": AGENT_ID},
}

class PingBenchmark:
    def __init__(self, iterations=100, concurrency=10):
        self.iterations = iterations
        self.concurrency = concurrency
        self.results = []
        
    async def ping_endpoint(self, session, method, endpoint, data=None):
        """Выполняет один ping-запрос"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"X-PORTA-TOKEN": TOKEN}
        
        if data:
            headers["Content-Type"] = "application/json"
            import json
            data = json.dumps(data)
        
        start_time = time.time()
        try:
            async with session.request(method, url, headers=headers, data=data) as response:
                response_time = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status": response.status,
                    "response_time": response_time,
                    "success": response.status == 200,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_benchmark(self):
        """Запускает ping-бенчмарк"""
        print(f"🏓 Запуск ping-бенчмарка: {self.iterations} запросов, {self.concurrency} параллельно")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Создаем задачи для всех запросов
            for i in range(self.iterations):
                method, endpoint = QUICK_ENDPOINTS[i % len(QUICK_ENDPOINTS)]
                data = POST_DATA.get(endpoint) if method == "POST" else None
                
                task = asyncio.create_task(
                    self.ping_endpoint(session, method, endpoint, data)
                )
                tasks.append(task)
            
            # Выполняем запросы с ограничением параллельности
            semaphore = asyncio.Semaphore(self.concurrency)
            
            async def limited_request(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[limited_request(task) for task in tasks])
            self.results = results
            self.print_report()
    
    def print_report(self):
        """Выводит отчет о бенчмарке"""
        successful_results = [r for r in self.results if r.get("success", False)]
        failed_results = [r for r in self.results if not r.get("success", False)]
        
        if not successful_results:
            print("❌ Все запросы завершились с ошибкой!")
            return
        
        response_times = [r["response_time"] for r in successful_results]
        
        # Статистика
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
        
        # Процентили
        sorted_times = sorted(response_times)
        p50 = sorted_times[len(sorted_times) * 50 // 100]
        p95 = sorted_times[len(sorted_times) * 95 // 100]
        p99 = sorted_times[len(sorted_times) * 99 // 100]
        
        print("\n" + "="*50)
        print("🏓 PING БЕНЧМАРК ОТЧЕТ")
        print("="*50)
        print(f"📊 Всего запросов: {len(self.results)}")
        print(f"✅ Успешных: {len(successful_results)}")
        print(f"❌ Ошибок: {len(failed_results)}")
        print(f"📈 Успешность: {(len(successful_results)/len(self.results)*100):.1f}%")
        
        print(f"\n⏱️  Время ответа (мс):")
        print(f"  Среднее: {avg_time*1000:.2f}")
        print(f"  Медиана: {median_time*1000:.2f}")
        print(f"  Минимум: {min_time*1000:.2f}")
        print(f"  Максимум: {max_time*1000:.2f}")
        print(f"  Стандартное отклонение: {std_dev*1000:.2f}")
        
        print(f"\n📊 Процентили (мс):")
        print(f"  P50: {p50*1000:.2f}")
        print(f"  P95: {p95*1000:.2f}")
        print(f"  P99: {p99*1000:.2f}")
        
        # Стабильность (коэффициент вариации)
        cv = (std_dev / avg_time * 100) if avg_time > 0 else 0
        print(f"\n🎯 Стабильность:")
        print(f"  Коэффициент вариации: {cv:.1f}%")
        if cv < 10:
            stability = "Отличная"
        elif cv < 20:
            stability = "Хорошая"
        elif cv < 30:
            stability = "Удовлетворительная"
        else:
            stability = "Нестабильная"
        print(f"  Оценка: {stability}")
        
        if failed_results:
            print(f"\n❌ Ошибки ({len(failed_results)}):")
            error_types = {}
            for error in failed_results:
                error_key = f"{error['method']} {error['endpoint']}"
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} раз")

async def main():
    """Основная функция"""
    print("🏓 Запуск ping-бенчмарка Porta")
    print(f"🎯 Цель: {100} запросов, {10} параллельно")
    
    benchmark = PingBenchmark(iterations=100, concurrency=10)
    await benchmark.run_benchmark()

if __name__ == "__main__":
    asyncio.run(main()) 