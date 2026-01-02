# Kenes Hub - Платформа реструктуризации долгов

## Описание проекта
Kenes Hub - это веб-приложение для Казахстана, предназначенное для автоматизации процессов реструктуризации долгов, медиации и взаимодействия с нотариусами.

## Технологический стек

### Backend
- **Python 3.11+**
- **Django 4.2+** - основной фреймворк
- **Django REST Framework** - API
- **Django Channels** - WebSocket поддержка
- **Celery** - фоновые задачи
- **Redis** - кэш и брокер сообщений
- **PostgreSQL** - основная БД
- **Gunicorn** - WSGI сервер

### Frontend
- **Next.js 14+** - React фреймворк
- **TypeScript** - типизация
- **Tailwind CSS** - стили
- **React Query** - кэширование запросов
- **Socket.io-client** - real-time соединения

### Инфраструктура
- **Docker** + **Docker Compose**
- **Nginx** - reverse proxy
- **GitHub Actions** - CI/CD
- **Let's Encrypt** - SSL сертификаты

## Структура проекта

```
kenes-hub/
├── backend/                 # Django backend
├── frontend/               # Next.js frontend
├── nginx/                  # Nginx конфигурация
├── docker/                 # Docker конфигурации
├── scripts/                # Скрипты развертывания
├── docs/                   # Документация
└── .github/workflows/      # CI/CD pipelines
```

## Установка и запуск

### Требования
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker и Docker Compose (опционально)

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd kenes-hub
```

2. Backend:
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Frontend:
```bash
cd frontend
npm install
npm run dev
```

4. Запуск с Docker:
```bash
docker-compose up -d
```

## Основные функции

- ✅ Прием заявок (WhatsApp, email, web-форма)
- ✅ Автоматическая классификация заявок
- ✅ Управление заявителями и статусами
- ✅ Генерация документов
- ✅ Электронная подпись (ЭЦП, SMS)
- ✅ AI-чатбот
- ✅ Портал участников с ролями
- ✅ Уведомления и рассылки
- ✅ Админ-панель с аналитикой
- ✅ Интеграции с внешними системами

## Документация API

API документация доступна по адресу: `http://localhost:8000/api/docs/`

## Разработка

### Стандарты кода
- PEP 8 для Python
- ESLint + Prettier для JavaScript/TypeScript
- Pre-commit hooks

### Тестирование
```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test
```

## Производственная среда

### Деплой
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Мониторинг
- Sentry - отслеживание ошибок
- Prometheus + Grafana - метрики
- ELK Stack - логирование

## Лицензия
MIT License