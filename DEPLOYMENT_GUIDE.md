# Руководство по развертыванию Kenes Hub

## Оглавление

1. [Требования](#требования)
2. [Установка](#установка)
3. [Конфигурация](#конфигурация)
4. [Запуск](#запуск)
5. [Проверка](#проверка)
6. [Производственная среда](#производственная-среда)
7. [Мониторинг](#мониторинг)
8. [Резервное копирование](#резервное-копирование)

## Требования

### Минимальные требования к серверу

- **CPU**: 4 vCPU
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 22.04 LTS (рекомендуется)
- **Network**: Статический IP-адрес

### Необходимое ПО

1. **Docker** (20.10+)
2. **Docker Compose** (2.0+)
3. **Git** (2.20+)
4. **Python** (3.11+) - для разработки
5. **Node.js** (18+) - для разработки

### Установка Docker и Docker Compose

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd kenes-hub
```

### 2. Настройка переменных окружения

Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`, указав необходимые значения:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (если используется внешняя БД)
DB_HOST=localhost
DB_NAME=kenes_hub
DB_USER=postgres
DB_PASSWORD=your-strong-password

# Redis
REDIS_URL=redis://redis:6379/1

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Provider
SMS_API_KEY=your-sms-api-key

# WhatsApp Business API
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_ID=your-phone-id

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

### 3. Запуск установочного скрипта

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Скрипт автоматически:
- Проверит наличие всех необходимых зависимостей
- Создаст и запустит Docker контейнеры
- Выполнит миграции базы данных
- Создаст суперпользователя
- Соберет статические файлы

## Конфигурация

### Настройка Nginx

Для производственной среды настройте Nginx конфигурацию в `nginx/conf.d/`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... остальная конфигурация
}
```

### Настройка SSL сертификатов

Используйте Let's Encrypt для бесплатных SSL сертификатов:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Настройка email

Для отправки email через Gmail:

1. Включите двухфакторную аутентификацию
2. Создайте пароль приложения
3. Используйте его в `EMAIL_HOST_PASSWORD`

## Запуск

### Быстрый запуск

```bash
docker-compose up -d
```

### Запуск с пересборкой

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Проверка

### Проверка статуса сервисов

```bash
docker-compose ps
```

### Проверка API

```bash
curl http://localhost:8000/api/
```

### Проверка frontend

Откройте браузер и перейдите по адресу `http://localhost:3000`

### Проверка админ-панели

Перейдите по адресу `http://localhost:8000/admin` и войдите используя учетные данные суперпользователя

## Производственная среда

### Настройка production docker-compose

Создайте `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
    command: gunicorn kenes_hub.wsgi:application --bind 0.0.0.0:8000 --workers 4
  
  frontend:
    command: npm start
```

### Запуск в production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Настройка systemd service

Создайте файл `/etc/systemd/system/kenes-hub.service`:

```ini
[Unit]
Description=Kenes Hub Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/kenes-hub
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Включите автозапуск:

```bash
sudo systemctl enable kenes-hub
sudo systemctl start kenes-hub
```

## Мониторинг

### Настройка Sentry

1. Создайте проект в Sentry
2. Установите SDK:

```bash
pip install sentry-sdk
cd frontend && npm install @sentry/nextjs
```

3. Настройте в `settings.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Настройка Prometheus и Grafana

Добавьте в `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Резервное копирование

### Автоматическое резервное копирование

Настройте cron job для автоматического резервного копирования:

```bash
# Откройте crontab
sudo crontab -e

# Добавьте строку для ежедневного бэкапа в 2:00 AM
0 2 * * * /opt/kenes-hub/scripts/backup.sh
```

### Ручное резервное копирование

```bash
chmod +x scripts/backup.sh
./scripts/backup.sh
```

### Восстановление из резервной копии

```bash
# Остановите сервисы
docker-compose down

# Восстановите базу данных
docker-compose exec -T db psql -U postgres kenes_hub < backup.sql

# Восстановите медиа файлы
tar -xzf backup-media.tar.gz -C ./backend/media/

# Запустите сервисы
docker-compose up -d
```

## Обновление

### Обновление приложения

```bash
# Остановите сервисы
docker-compose down

# Получите последние изменения
git pull origin main

# Пересоберите и запустите
docker-compose build --no-cache
docker-compose up -d
```

### Обновление зависимостей

```bash
# Backend
docker-compose exec backend pip install -r requirements.txt

# Frontend
docker-compose exec frontend npm update
```

## Устранение неполадок

### Проблемы с базой данных

```bash
# Проверка логов PostgreSQL
docker-compose logs db

# Подключение к базе данных
docker-compose exec db psql -U postgres kenes_hub
```

### Проблемы с backend

```bash
# Проверка статуса миграций
docker-compose exec backend python manage.py showmigrations

# Запуск миграций вручную
docker-compose exec backend python manage.py migrate
```

### Проблемы с frontend

```bash
# Пересборка frontend
docker-compose exec frontend npm run build
```

## Поддержка

### Контакты

- **Email**: support@kenes-hub.kz
- **Телефон**: +7 (777) 123-45-67

### Документация

- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Documentation**: http://localhost:8000/admin/doc/

---

**Примечание**: Это руководство предназначено для опытных системных администраторов и разработчиков. При развертывании в производственной среде обязательно следуйте принципам безопасности и настройте мониторинг.