# Roommate Finder Web

Веб-версия приложения для поиска соседей по комнате с алгоритмами совместимости.

## Структура проекта

```
web/
├── backend/          # FastAPI сервер
│   ├── main.py       # Основное приложение
│   ├── models.py     # Модели данных
│   ├── database.py   # Работа с SQLite
│   ├── algorithms.py # Алгоритмы совместимости
│   ├── config.py     # Конфигурация
│   └── requirements.txt
└── frontend/         # React приложение
    ├── src/
    │   ├── api/      # API клиенты
    │   ├── pages/    # Страницы
    │   ├── App.jsx   # Главный компонент
    │   └── index.css # Стили
    ├── index.html
    └── package.json
```

## Запуск

### Backend

```bash
cd web/backend
pip install -r requirements.txt
python main.py
```

Сервер запустится на http://localhost:8000

### Frontend

```bash
cd web/frontend
npm install
npm run dev
```

Приложение запустится на http://localhost:3000

## API Endpoints

### Авторизация
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход

### Профиль
- `GET /api/profile/me` - Получить мой профиль
- `PUT /api/profile/me` - Обновить профиль
- `GET /api/profile/{user_id}` - Получить профиль пользователя

### Поиск (свайпы)
- `GET /api/candidates` - Получить кандидатов
- `POST /api/swipe` - Создать свайп

### Матчи
- `GET /api/matches` - Получить матчи

### Сообщения
- `POST /api/messages/{receiver_id}` - Отправить сообщение
- `GET /api/messages/{other_user_id}` - Получить переписку
- `GET /api/contacts` - Получить контакты

### Совместимость
- `GET /api/compatibility/{candidate_id}` - Рассчитать совместимость

## Алгоритм совместимости

Совместимость рассчитывается по 7 категориям с разными весами:
- Бюджет (15%)
- Район (15%)
- Чистота (20%)
- Шум (15%)
- Распорядок дня (15%)
- Привычки (10%)
- Личность (10%)

## Тестовый вход

Администратор:
- Логин: `admin`
- Пароль: `admin123`
