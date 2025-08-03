#!/usr/bin/env python3
import subprocess
import json
import datetime
import os
import statistics
import re

# === Конфигурация ===
RPS = int(os.getenv("RPS", 5))               # Запросов в секунду
DURATION = int(os.getenv("DURATION", 60))    # Длительность в секундах
LOG_DIR = "./logs/daily_metrics"

# === Подготовка ===
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
filename = f"{LOG_DIR}/{now.strftime('%Y-%m-%d')}.json"
os.makedirs(LOG_DIR, exist_ok=True)

# === Запуск stress-теста ===
print(f"📊 Запуск stress-теста: {RPS} RPS на {DURATION} секунд...")
result = subprocess.run(
    ["python3", "scripts/stress_test.py"],
    capture_output=True,
    text=True,
    env={**os.environ, "RPS": str(RPS), "DURATION": str(DURATION)}
)

# === Парсинг вывода ===
pattern = r"\[(.*?)\]\s+(\d{3})\s+-\s+(\d+)ms"
matches = re.findall(pattern, result.stdout)
latencies = [int(ms) for _, status, ms in matches if status == "200"]

# === Расчёты ===
summary = {
    "timestamp": timestamp,
    "rps": RPS,
    "duration_sec": DURATION,
    "requests_sent": len(matches),
    "successful": len(latencies),
    "errors": len(matches) - len(latencies),
    "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else None,
    "p95_latency_ms": round(statistics.quantiles(latencies, n=100)[94]) if len(latencies) >= 20 else None,
    "p99_latency_ms": round(statistics.quantiles(latencies, n=100)[98]) if len(latencies) >= 20 else None,
    "cv_latency": round(statistics.stdev(latencies) / statistics.mean(latencies) * 100, 2) if len(latencies) >= 2 else None,
    "raw_output": result.stdout.strip(),
    "returncode": result.returncode
}

# === Сохраняем отчёт ===
with open(filename, "w") as f:
    json.dump(summary, f, indent=2)

print(f"✅ Диагностика завершена.\n📁 Отчёт сохранён в: {filename}")
if summary["cv_latency"]:
    print(f"📈 CV (коэффициент вариации): {summary['cv_latency']}%")
