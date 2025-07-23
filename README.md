# MonitoringSystem

## Обновленная система мониторинга

### Компоненты:
- **Prometheus v2.48.1** - сбор и хранение метрик
- **Grafana v10.2.3** - визуализация данных
- **Node Exporter v1.7.0** - метрики системы Linux
- **Blackbox Exporter v0.24.0** - мониторинг доступности сервисов

### Оптимизации:
- Оптимизированные интервалы scrape (15s вместо 5s)
- Добавлено WAL сжатие в Prometheus
- Улучшенная конфигурация Node Exporter
- Расширенные модули Blackbox Exporter

### Запуск:
```bash
docker-compose up -d
```

### Доступ:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Node Exporter: http://localhost:9100
- Blackbox Exporter: http://localhost:9115
