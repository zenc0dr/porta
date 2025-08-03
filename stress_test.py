#!/usr/bin/env python3
"""
Скрипт для стресс-тестирования Porta
Имитирует умеренную нагрузку: 30 запросов в минуту
"""

import asyncio
import aiohttp
import time
import random
import json
from datetime import datetime

# Конфигурация
BASE_URL = "http://localhost:8111"
TOKEN = "test123"
AGENT_ID = "stress-test-agent"

# Endpoints для тестирования
ENDPOINTS = [
    ("GET", "/meta"),
    ("GET", "/public_url"),
    ("POST", "/agent/status"),
    ("POST", "/run_bash"),
    ("POST", "/agent/list"),
    ("POST", "/agent/history"),
    ("POST", "/agent/pipeline"),
]

# Данные для POST запросов
POST_DATA = {
    "/agent/status": {"agent_id": AGENT_ID},
    "/run_bash": {"cmd": "echo stress test", "agent_id": AGENT_ID},
    "/agent/list": {"limit": 10},
    "/agent/history": {"agent_id": AGENT_ID, "limit": 5},
    "/agent/pipeline": {
        "agent_id": AGENT_ID,
        "commands": ["echo step1", "echo step2"],
        "timeout": 30
    }
}

class StressTest:
    def __init__(self, duration_minutes=5, requests_per_minute=30):
        self.duration_minutes = duration_minutes
        self.requests_per_minute = requests_per_minute
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    async def make_request(self, session, method, endpoint, data=None):
        """Выполняет один запрос и измеряет время ответа"""
        url = f"{BASE_URL}{endpoint}"
        headers = {"X-PORTA-TOKEN": TOKEN}
        
        if data:
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        
        start_time = time.time()
        try:
            async with session.request(method, url, headers=headers, data=data) as response:
                response_time = time.time() - start_time
                status = response.status
                content = await response.text()
                
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status": status,
                    "response_time": response_time,
                    "success": status == 200,
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
    
    async def run_stress_test(self):
        """Запускает стресс-тест"""
        print(f"🚀 Запуск стресс-теста: {self.duration_minutes} минут, {self.requests_per_minute} запросов/мин")
        print(f"📊 Всего запросов: {self.duration_minutes * self.requests_per_minute}")
        
        self.start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Создаем задачи для всех запросов
            for minute in range(self.duration_minutes):
                for request in range(self.requests_per_minute):
                    # Случайный endpoint
                    method, endpoint = random.choice(ENDPOINTS)
                    data = POST_DATA.get(endpoint) if method == "POST" else None
                    
                    # Случайная задержка в пределах минуты
                    delay = (minute * 60 + request * (60 / self.requests_per_minute)) + random.uniform(0, 2)
                    
                    task = asyncio.create_task(
                        self.delayed_request(session, method, endpoint, data, delay)
                    )
                    tasks.append(task)
            
            # Ждем завершения всех задач
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for result in results:
                if isinstance(result, dict):
                    self.results.append(result)
                    if not result.get("success", False):
                        self.errors.append(result)
        
        self.end_time = time.time()
        self.print_report()
    
    async def delayed_request(self, session, method, endpoint, data, delay):
        """Выполняет запрос с задержкой"""
        await asyncio.sleep(delay)
        return await self.make_request(session, method, endpoint, data)
    
    def print_report(self):
        """Выводит отчет о тестировании"""
        total_time = self.end_time - self.start_time
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.get("success", False)])
        failed_requests = len(self.errors)
        
        response_times = [r["response_time"] for r in self.results if "response_time" in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        print("\n" + "="*60)
        print("📊 ОТЧЕТ О СТРЕСС-ТЕСТЕ")
        print("="*60)
        print(f"⏱️  Общее время: {total_time:.2f} секунд")
        print(f"📈 Всего запросов: {total_requests}")
        print(f"✅ Успешных: {successful_requests}")
        print(f"❌ Ошибок: {failed_requests}")
        print(f"📊 Успешность: {(successful_requests/total_requests*100):.1f}%")
        print(f"⚡ Среднее время ответа: {avg_response_time*1000:.2f}ms")
        print(f"🚀 Минимальное время: {min_response_time*1000:.2f}ms")
        print(f"🐌 Максимальное время: {max_response_time*1000:.2f}ms")
        
        if self.errors:
            print(f"\n❌ Ошибки ({len(self.errors)}):")
            for error in self.errors[:5]:  # Показываем первые 5 ошибок
                print(f"  - {error['method']} {error['endpoint']}: {error.get('error', error.get('status'))}")
        
        # Статистика по endpoint'ам
        endpoint_stats = {}
        for result in self.results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"count": 0, "times": [], "errors": 0}
            
            endpoint_stats[endpoint]["count"] += 1
            if "response_time" in result:
                endpoint_stats[endpoint]["times"].append(result["response_time"])
            if not result.get("success", False):
                endpoint_stats[endpoint]["errors"] += 1
        
        print(f"\n📋 Статистика по endpoint'ам:")
        for endpoint, stats in endpoint_stats.items():
            avg_time = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
            error_rate = (stats["errors"] / stats["count"] * 100) if stats["count"] > 0 else 0
            print(f"  {endpoint}: {stats['count']} запросов, "
                  f"среднее время {avg_time*1000:.2f}ms, "
                  f"ошибок {error_rate:.1f}%")

async def main():
    """Основная функция"""
    print("🧪 Запуск стресс-теста Porta")
    print(f"🎯 Цель: {5} минут, {30} запросов/мин")
    
    stress_test = StressTest(duration_minutes=5, requests_per_minute=30)
    await stress_test.run_stress_test()

if __name__ == "__main__":
    asyncio.run(main()) 