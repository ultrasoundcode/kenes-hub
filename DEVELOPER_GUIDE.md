# Руководство разработчика Kenes Hub

## Быстрый старт для новичков

### Шаг 1: Установка необходимого ПО

#### На macOS:

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Python
brew install python@3.11

# Установка Node.js
brew install node

# Установка PostgreSQL
brew install postgresql
brew services start postgresql

# Установка Redis
brew install redis
brew services start redis

# Установка Git
git --version  # должно быть уже установлено
```

#### На Windows:

1. Установите Python 3.11 с [python.org](https://www.python.org/downloads/)
2. Установите Node.js 18+ с [nodejs.org](https://nodejs.org/)
3. Установите PostgreSQL с [postgresql.org](https://www.postgresql.org/download/windows/)
4. Установите Redis с [github.com/tporadowski/redis](https://github.com/tporadowski/redis/releases)
5. Установите Git с [git-scm.com](https://git-scm.com/download/win)

#### На Linux (Ubuntu/Debian):

```bash
# Обновление пакетов
sudo apt update

# Установка Python
sudo apt install python3.11 python3.11-venv python3-pip

# Установка Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib

# Установка Redis
sudo apt install redis-server

# Установка Git
sudo apt install git
```

### Шаг 2: Настройка Git и GitHub

```bash
# Настройка Git
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"

# Создание SSH ключа для GitHub
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub  # скопируйте вывод

# Добавьте ключ в GitHub:
# 1. Перейдите на github.com/settings/keys
# 2. Нажмите "New SSH key"
# 3. Вставьте скопированный ключ
```

### Шаг 3: Клонирование проекта

```bash
git clone git@github.com:your-username/kenes-hub.git
cd kenes-hub
```

### Шаг 4: Настройка backend

```bash
cd backend

# Создание виртуального окружения
python3.11 -m venv venv

# Активация виртуального окружения
# На macOS/Linux:
source venv/bin/activate
# На Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Создание базы данных
createdb kenes_hub  # macOS/Linux
# или
createdb -U postgres kenes_hub  # с указанием пользователя

# Выполнение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера разработки
python manage.py runserver
```

Backend будет доступен по адресу: http://localhost:8000

### Шаг 5: Настройка frontend

В новом терминале:

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск сервера разработки
npm run dev
```

Frontend будет доступен по адресу: http://localhost:3000

### Шаг 6: Установка Redis

Убедитесь, что Redis запущен:

```bash
# macOS
redis-server

# Linux
sudo systemctl start redis

# Windows (через Services или командная строка от администратора)
redis-server.exe
```

### Шаг 7: Запуск Celery worker (опционально)

В новом терминале:

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate     # Windows

celery -A kenes_hub worker -l info
```

## Структура проекта

```
kenes-hub/
├── backend/                 # Django backend
│   ├── apps/               # Приложения Django
│   │   ├── accounts/       # Пользователи и аутентификация
│   │   ├── applications/   # Заявки
│   │   ├── documents/      # Документы
│   │   ├── notifications/  # Уведомления
│   │   ├── chat/           # Чат
│   │   ├── ai/             # AI помощник
│   │   └── integrations/   # Внешние интеграции
│   ├── kenes_hub/          # Настройки Django
│   ├── media/              # Медиа файлы
│   ├── static/             # Статические файлы
│   ├── requirements.txt    # Зависимости Python
│   └── manage.py           # Django CLI
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App Router (Next.js 13+)
│   │   ├── components/    # React компоненты
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API сервисы
│   │   ├── types/         # TypeScript типы
│   │   └── utils/         # Утилиты
│   ├── package.json
│   └── tsconfig.json
├── docker/                 # Docker конфигурации
├── nginx/                  # Nginx конфигурации
├── scripts/                # Скрипты
└── docs/                   # Документация
```

## Основные команды разработки

### Backend (Django)

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск тестов
python manage.py test

# Запуск сервера
python manage.py runserver

# Запуск shell
python manage.py shell

# Проверка кода (lint)
flake8 apps/
black apps/
```

### Frontend (Next.js)

```bash
# Запуск сервера разработки
npm run dev

# Сборка для production
npm run build

# Запуск production сервера
npm start

# Проверка типов
npm run type-check

# Lint
npm run lint

# Форматирование кода
npm run format
```

### Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка контейнеров
docker-compose build --no-cache

# Выполнение команд в контейнере
docker-compose exec backend python manage.py migrate
docker-compose exec frontend npm install
```

## Работа с Git

### Базовые команды

```bash
# Просмотр статуса
git status

# Добавление файлов
git add .
git add <filename>

# Коммит изменений
git commit -m "Описание изменений"

# Пуш в репозиторий
git push origin main

# Получение изменений
git pull origin main

# Создание новой ветки
git checkout -b feature/new-feature

# Переключение на ветку
git checkout main

# Слияние веток
git merge feature/new-feature
```

### Рабочий процесс (Git Flow)

1. **Создайте feature ветку** от main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-new-feature
   ```

2. **Работайте над функцией** и делайте коммиты:
   ```bash
   git add .
   git commit -m "Add: новая функция для заявок"
   ```

3. **Пушьте ветку** на GitHub:
   ```bash
   git push origin feature/my-new-feature
   ```

4. **Создайте Pull Request** на GitHub

5. **После одобрения** - смержите в main

## Отладка и troubleshooting

### Backend

#### Проблема: "Database connection failed"

**Решение:**
```bash
# Проверьте, запущен ли PostgreSQL
sudo systemctl status postgresql

# Запустите PostgreSQL
sudo systemctl start postgresql

# Создайте пользователя и базу данных
sudo -u postgres psql
CREATE USER youruser WITH PASSWORD 'yourpassword';
CREATE DATABASE kenes_hub OWNER youruser;
\q
```

#### Проблема: "Module not found"

**Решение:**
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### Frontend

#### Проблема: "npm install зависает"

**Решение:**
```bash
# Очистите кэш npm
npm cache clean --force

# Удалите node_modules и package-lock.json
rm -rf node_modules package-lock.json

# Установите зависимости заново
npm install
```

#### Проблема: "TypeScript errors"

**Решение:**
```bash
# Проверьте типы
npm run type-check

# Исправьте ошибки в соответствующих файлах
# Запустите сервер разработки для более детальной информации
npm run dev
```

## Рекомендуемые инструменты

### Редакторы кода

1. **VS Code** (настоятельно рекомендуется)
   - Расширения для Python: Python, Django, Black Formatter
   - Расширения для JavaScript/TypeScript: ESLint, Prettier, Bracket Pair Colorizer
   - Расширения для React: ES7+ React/Redux/React-Native snippets

2. **PyCharm** (для backend разработки)

3. **WebStorm** (для frontend разработки)

### Утилиты

- **Postman** или **Insomnia** - для тестирования API
- **DBeaver** или **pgAdmin** - для работы с БД
- **Redis Insight** - для работы с Redis
- **Docker Desktop** - для управления контейнерами

## Полезные ресурсы для изучения

### Django
- [Official Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple is Better Than Complex](https://simpleisbetterthancomplex.com/)

### React/Next.js
- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

### Docker
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Git
- [Git Book](https://git-scm.com/book)
- [GitHub Guides](https://guides.github.com/)

## Получение помощи

Если у вас возникли вопросы:

1. Проверьте документацию в папке `docs/`
2. Проверьте логи сервисов
3. Задайте вопрос в командном чате
4. Создайте issue на GitHub

## Следующие шаги

После успешной установки:

1. **Изучите структуру проекта**
2. **Попробуйте создать простую функцию**
3. **Прочитайте документацию API**
4. **Поэкспериментируйте с админ-панелью**
5. **Присоединитесь к команде разработки**

Удачи в разработке! 🚀