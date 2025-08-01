## 🔐 Руководство по безопасности системы мониторинга

## Реализованные меры безопасности

### 1. ⚠️ Prometheus (BEZ авторизации)
- **Статус**: Нет авторизации
- **Доступ**: Открытый доступ к http://localhost:9090
- **Риск**: Высокий - любой может получить доступ

### 2. 🔒 Grafana Security Settings
- **Админ логин**: `admin`
- **Админ пароль**: `StrongAdminPassword123!`
- Отключена анонимная авторизация
- Отключена самостоятельная регистрация пользователей
- Установлен секретный ключ для сессий

### 3. 🚦 Доступ к сервисам
После применения настроек безопасности:

#### Prometheus:
- URL: http://localhost:9090
- Открытый доступ (без авторизации)

#### Grafana:
- URL: http://localhost:3000
- Требует вход (admin/StrongAdminPassword123!)

#### Node Exporter:
- URL: http://localhost:9100
- Не защищен (рекомендуется ограничить доступ через firewall)

#### Blackbox Exporter:
- URL: http://localhost:9115
- Не защищен (рекомендуется ограничить доступ через firewall)

## 🔄 Применение изменений

1. Остановите текущие контейнеры:
```bash
docker-compose down
```

2. Запустите с новыми настройками:
```bash
docker-compose up -d
```

## 🔧 Дополнительные рекомендации по безопасности

### 1. Изменение паролей по умолчанию
**ВАЖНО**: Обязательно измените пароли по умолчанию перед использованием в production!

#### Для Prometheus:
Создайте новый хеш пароля:
```bash
# Установите apache2-utils (Ubuntu/Debian) или httpd-tools (CentOS/RHEL)
htpasswd -nBC 12 "" | tr -d ':\n'
```
Замените хеш в файле `prometheus/web.yml`

#### Для Grafana:
Измените переменные окружения в `docker-compose.yml`:
```yaml
- GF_SECURITY_ADMIN_PASSWORD=ВАШ_НОВЫЙ_ПАРОЛЬ
- GF_SECURITY_SECRET_KEY=ваш-секретный-ключ-минимум-32-символа
```

### 2. 🌐 Настройка HTTPS
Для production использования настройте SSL/TLS:

#### Для Prometheus:
Раскомментируйте в `prometheus/web.yml`:
```yaml
tls_server_config:
  cert_file: /etc/prometheus/prometheus.crt
  key_file: /etc/prometheus/prometheus.key
```

#### Для Grafana:
Добавьте в переменные окружения:
```yaml
- GF_SERVER_PROTOCOL=https
- GF_SERVER_CERT_FILE=/etc/ssl/certs/grafana.crt
- GF_SERVER_CERT_KEY=/etc/ssl/private/grafana.key
```

### 3. 🔥 Настройка Firewall
Ограничьте доступ к портам:

```bash
# Разрешить доступ только с определенных IP
sudo ufw allow from 192.168.1.0/24 to any port 9090
sudo ufw allow from 192.168.1.0/24 to any port 3000

# Заблокировать прямой доступ к Node Exporter и Blackbox
sudo ufw deny 9100
sudo ufw deny 9115
```

### 4. 📊 Мониторинг безопасности
Добавьте алерты для отслеживания:
- Неудачных попыток входа
- Необычной активности
- Доступа с неизвестных IP адресов

### 5. 🔄 Регулярное обслуживание
- Регулярно обновляйте все компоненты
- Меняйте пароли каждые 90 дней
- Проверяйте логи на подозрительную активность
- Создавайте резервные копии конфигураций

## ⚠️ Предупреждения безопасности

1. **НЕ используйте пароли по умолчанию в production!**
2. **НЕ коммитьте пароли в git репозиторий!**
3. **НЕ оставляйте сервисы без аутентификации в публичных сетях!**
4. **Используйте HTTPS для всех production развертываний!**

## 📞 Что делать в случае компрометации

1. Немедленно измените все пароли
2. Перезапустите все сервисы
3. Проверьте логи на подозрительную активность
4. Обновите все компоненты до последних версий
5. Рассмотрите возможность изменения портов по умолчанию

---
**Помните**: Безопасность - это процесс, а не состояние. Регулярно пересматривайте и обновляйте настройки безопасности.
