#!/bin/bash

# === Настройка ежедневной диагностики Porta ===

echo "🔧 Настройка ежедневной диагностики Porta..."

# Создаём папку для логов
mkdir -p logs/daily_metrics

# Создаём systemd timer (если доступен)
if command -v systemctl &> /dev/null; then
    echo "📅 Создание systemd timer..."
    
    # Создаём service файл
    cat > /tmp/porta-diagnostics.service << EOF
[Unit]
Description=Porta Daily Diagnostics
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/scripts/run_diagnostics.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Создаём timer файл
    cat > /tmp/porta-diagnostics.timer << EOF
[Unit]
Description=Run Porta diagnostics daily
Requires=porta-diagnostics.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Копируем файлы в systemd
    sudo cp /tmp/porta-diagnostics.service /etc/systemd/system/
    sudo cp /tmp/porta-diagnostics.timer /etc/systemd/system/
    
    # Включаем и запускаем timer
    sudo systemctl daemon-reload
    sudo systemctl enable porta-diagnostics.timer
    sudo systemctl start porta-diagnostics.timer
    
    echo "✅ Systemd timer настроен"
    echo "📊 Статус: systemctl status porta-diagnostics.timer"
    echo "📋 Логи: journalctl -u porta-diagnostics.service"
    
else
    echo "⚠️  Systemd недоступен, используйте cron"
    echo "📝 Добавьте в crontab:"
    echo "0 9 * * * cd $(pwd) && python3 scripts/run_diagnostics.py"
fi

echo ""
echo "🎯 Ручной запуск: python3 scripts/run_diagnostics.py"
echo "📁 Логи: logs/daily_metrics/"
echo "📊 Отчёт: docs/daily_metrics_index.md" 