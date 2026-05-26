import sqlite3
from datetime import datetime, timedelta
import random
import os
import sys

# Добавляем родительскую директорию в path для импорта config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH

# Настройки
print(f"Используемая база данных: {DB_PATH}")

def create_tables():
    """Создает все необходимые таблицы в базе данных"""
    # Удаляем старую базу данных для чистого старта
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Старая база данных {DB_PATH} удалена.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей (используем phone как логин)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0
        )
    """)
    
    # Таблица профилей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            occupation TEXT,
            contact_info TEXT,
            photo_path TEXT,
            budget_min INTEGER DEFAULT 5000,
            budget_max INTEGER DEFAULT 50000,
            preferred_districts TEXT,
            housing_type TEXT,
            rental_period TEXT,
            daily_schedule TEXT,
            cleanliness_level INTEGER DEFAULT 5,
            noise_tolerance INTEGER DEFAULT 5,
            smoking INTEGER DEFAULT 0,
            alcohol INTEGER DEFAULT 0,
            personality_type INTEGER DEFAULT 5,
            hobbies TEXT,
            has_pets INTEGER DEFAULT 0,
            preferred_neighbor_gender TEXT,
            neighbor_age_min INTEGER DEFAULT 18,
            neighbor_age_max INTEGER DEFAULT 60,
            important_criteria TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Таблица свайпов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_user_id INTEGER NOT NULL,
            direction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, target_user_id)
        )
    """)
    
    # Таблица мэтчей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (user2_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Таблица сообщений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print("Таблицы созданы.")

def seed_database():
    # Сначала создаем все таблицы (это удалит старую БД и создаст новую)
    create_tables()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Создаем пользователей (используем phone как логин)
    # Пароли хранятся в открытом виде (тестовый стенд)
    users_data = [
        ("admin", "admin123", "active"),      # admin
        ("+79001112233", "123456", "active"),  # alice
        ("+79001112234", "123456", "active"),  # bob
        ("+79001112235", "123456", "active"),  # charlie
        ("+79001112236", "123456", "active"),  # diana
        ("+79001112237", "123456", "active"),  # eve
        ("+79001112238", "123456", "active"),  # frank
    ]

    user_ids = {}
    user_phones = ["admin", "+79001112233", "+79001112234", "+79001112235", "+79001112236", "+79001112237", "+79001112238"]
    usernames = ["admin", "alice", "bob", "charlie", "diana", "eve", "frank"]
    
    for i, (phone, password, status) in enumerate(users_data):
        is_admin = 1 if phone == "admin" else 0
        cursor.execute(
            "INSERT INTO users (phone, password_hash, created_at, is_active, is_admin) VALUES (?, ?, ?, ?, ?)",
            (phone, password, datetime.now().isoformat(), 1 if status == "active" else 0, is_admin)
        )
        user_ids[usernames[i]] = cursor.lastrowid

    print(f"Создано пользователей: {len(user_ids)}")

    # 2. Создаем профили с разными характеристиками для проверки алгоритмов
    profiles_data = [
        # Alice: Чистюля, ранний подъем, бюджет 50к, Центр
        (user_ids["alice"], "Алиса, 23", 23, "female", "Студентка", "", "", 5000, 50000, "[]", "", "", "", 5, 5, False, False, 1, "[]", False, "", 18, 60, "[]"),
        # Bob: Спокойный, бюджет 50к, Центр (Мэтч с Алисой)
        (user_ids["bob"], "Борис, 24", 24, "male", "Разработчик", "", "", 5000, 55000, "[]", "", "", "", 4, 4, False, False, 2, "[]", False, "", 18, 60, "[]"),
        # Charlie: Тусовщик, шумный, бюджет 30к, Север (Не мэтч с Алисой)
        (user_ids["charlie"], "Чарли, 22", 22, "male", "Музыкант", "", "", 5000, 30000, "[]", "", "", "", 2, 1, False, False, 5, "[]", False, "", 18, 60, "[]"),
        # Diana: Умеренная, бюджет 40к, Юг
        (user_ids["diana"], "Диана, 25", 25, "female", "Дизайнер", "", "", 5000, 40000, "[]", "", "", "", 3, 3, False, False, 3, "[]", False, "", 18, 60, "[]"),
        # Eve: Чистюля, бюджет 60к, Запад (Потенциальный мэтч с Алисой)
        (user_ids["eve"], "Ева, 23", 23, "female", "Маркетолог", "", "", 5000, 60000, "[]", "", "", "", 5, 4, False, False, 2, "[]", False, "", 18, 60, "[]"),
        # Frank: Бюджетник, любой район
        (user_ids["frank"], "Франк, 21", 21, "male", "Студент", "", "", 5000, 25000, "[]", "", "", "", 2, 2, False, False, 4, "[]", False, "", 18, 60, "[]"),
    ]

    profile_ids = {}
    for data in profiles_data:
        uid = data[0]
        cursor.execute("""
            INSERT OR REPLACE INTO profiles (user_id, full_name, age, gender, occupation, contact_info, photo_path, 
            budget_min, budget_max, preferred_districts, housing_type, rental_period, daily_schedule, 
            cleanliness_level, noise_tolerance, smoking, alcohol, personality_type, hobbies, 
            has_pets, preferred_neighbor_gender, neighbor_age_min, neighbor_age_max, important_criteria)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        profile_ids[uid] = cursor.lastrowid

    print(f"Создано профилей: {len(profile_ids)}")

    # 3. Создаем свайпы и мэтчи
    now = datetime.now()
    
    # Мэтч между Alice и Bob (взаимные лайки)
    # Alice likes Bob
    cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["alice"], user_ids["bob"], "right", now.isoformat()))
    # Bob likes Alice
    cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["bob"], user_ids["alice"], "right", (now - timedelta(hours=1)).isoformat()))
    # Создаем мэтч
    cursor.execute("INSERT OR REPLACE INTO matches (user1_id, user2_id, created_at) VALUES (?, ?, ?)",
                   (user_ids["alice"], user_ids["bob"], now.isoformat()))
    
    # Мэтч между Alice и Eve (взаимные лайки)
    cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["alice"], user_ids["eve"], "right", (now - timedelta(days=1)).isoformat()))
    cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["eve"], user_ids["alice"], "right", (now - timedelta(days=1, hours=2)).isoformat()))
    cursor.execute("INSERT OR REPLACE INTO matches (user1_id, user2_id, created_at) VALUES (?, ?, ?)",
                   (user_ids["alice"], user_ids["eve"], (now - timedelta(days=1)).isoformat()))

    # Charlie лайкает Diana, но без ответа (нет мэтча)
    cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                   (user_ids["charlie"], user_ids["diana"], "right", now.isoformat()))
    
    # Frank лайкает всех, но ему никто не лайкнул в ответ
    for uid in [user_ids["alice"], user_ids["bob"], user_ids["diana"]]:
        cursor.execute("INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at) VALUES (?, ?, ?, ?)",
                       (user_ids["frank"], uid, "right", now.isoformat()))

    print("Свайпы и мэтчи созданы.")

    # 4. Добавляем сообщения в чат между Alice и Bob
    messages = [
        (user_ids["alice"], user_ids["bob"], "Привет! Я увидела твой профиль, нам нравится один район.", (now - timedelta(minutes=30)).isoformat()),
        (user_ids["bob"], user_ids["alice"], "Привет, Алиса! Да, Центр очень удобен для работы. Ты давно ищешь соседа?", (now - timedelta(minutes=25)).isoformat()),
        (user_ids["alice"], user_ids["bob"], "Пару дней. Важно, чтобы человек был аккуратным. Как у тебя с этим?", (now - timedelta(minutes=20)).isoformat()),
        (user_ids["bob"], user_ids["alice"], "Я довольно чистоплотен, убираюсь по выходным. А ты любишь гостей?", (now - timedelta(minutes=15)).isoformat()),
        (user_ids["alice"], user_ids["bob"], "Редко, в основном тихие вечера. Может встретимся посмотреть квартиру?", (now - timedelta(minutes=10)).isoformat()),
        (user_ids["bob"], user_ids["alice"], "Отличная идея! Я свободен завтра после 18:00.", (now - timedelta(minutes=5)).isoformat()),
    ]

    for sender_id, receiver_id, text, timestamp in messages:
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, timestamp, is_read)
            VALUES (?, ?, ?, ?, ?)
        """, (sender_id, receiver_id, text, timestamp, 1 if timestamp < (now - timedelta(minutes=10)).isoformat() else 0))

    print("Сообщения добавлены.")

    conn.commit()
    conn.close()
    print("\n✅ База данных успешно наполнена тестовыми данными!")
    print("\n=== ТЕСТОВЫЕ УЧЕТНЫЕ ДАННЫЕ ===")
    print("Администратор: login=admin, password=admin123")
    print("\nОбычные пользователи (пароль 123456 для всех):")
    print("  Алиса: +79001112233 (есть 2 мэтча, переписка с Борисом)")
    print("  Борис: +79001112234")
    print("  Чарли: +79001112235")
    print("  Диана: +79001112236")
    print("  Ева:   +79001112237")
    print("  Франк: +79001112238")
    print("\n⚠️  Пароли хранятся в открытом виде (тестовый стенд)")

if __name__ == "__main__":
    seed_database()
