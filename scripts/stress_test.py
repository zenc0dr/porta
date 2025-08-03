import httpx
import asyncio
import random
import time

# Конфигурация
PORTA_URL = "http://localhost:8111"
AGENT_ID = "stress-test-agent"
TOKEN = "test123"
HEADERS = {"X-PORTA-TOKEN": TOKEN, "Content-Type": "application/json"}

# Тестируемые endpoint'ы
ENDPOINTS = [
    {"url": "/agent/status", "method": "POST", "json": lambda: {"agent_id": AGENT_ID}},
    {"url": "/run_bash", "method": "POST", "json": lambda: {"cmd": "echo hello", "agent_id": AGENT_ID}},
    {"url": "/agent/pipeline", "method": "POST", "json": lambda: {"agent_id": AGENT_ID, "commands": ["echo 1", "echo 2"], "timeout": 10}},
]

async def send_request(client, endpoint):
    url = PORTA_URL + endpoint["url"]
    json_payload = endpoint["json"]()
    try:
        start = time.time()
        resp = await client.request(endpoint["method"], url, headers=HEADERS, json=json_payload, timeout=10.0)
        duration = (time.time() - start) * 1000  # в мс
        print(f"[{endpoint['url']}] {resp.status_code} - {int(duration)}ms")
    except Exception as e:
        print(f"[{endpoint['url']}] ERROR: {e}")

async def run_stress_test(rps=1, duration_seconds=60):
    print(f"⚡ Начало stress-теста: {rps} RPS на {duration_seconds} секунд")
    async with httpx.AsyncClient() as client:
        for _ in range(duration_seconds):
            tasks = [send_request(client, random.choice(ENDPOINTS)) for _ in range(rps)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_stress_test(rps=5, duration_seconds=60))
