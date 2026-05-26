"""
Модуль работы с базой данных для веб-версии
"""
import sqlite3
import json
import os
import shutil
from datetime import datetime
from typing import List, Optional, Tuple
from contextlib import contextmanager
from config import DB_PATH, BACKUP_DIR, ADMIN_PHONE, ADMIN_PASSWORD
from models import User, Profile, Swipe, Match, Advertisement, Message, CompatibilityResult, SystemLog


class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self._initialize_database()
        self._create_admin_user()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _initialize_database(self):
        """Инициализация таблиц БД"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    is_admin INTEGER DEFAULT 0
                )
            ''')

            # Таблица профилей
            cursor.execute('''
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
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Таблица свайпов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS swipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    target_user_id INTEGER NOT NULL,
                    direction TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (target_user_id) REFERENCES users(id),
                    UNIQUE(user_id, target_user_id)
                )
            ''')

            # Таблица матчей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user1_id) REFERENCES users(id),
                    FOREIGN KEY (user2_id) REFERENCES users(id)
                )
            ''')

            # Таблица объявлений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS advertisements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Таблица сообщений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    FOREIGN KEY (receiver_id) REFERENCES users(id)
                )
            ''')

            # Таблица совместимости
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compatibility_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    compatibility_score REAL NOT NULL,
                    details TEXT,
                    calculated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (candidate_id) REFERENCES users(id)
                )
            ''')

            # Таблица логов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')

            conn.commit()

    def _create_admin_user(self):
        """Создание администратора по умолчанию"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM users WHERE phone = ?', (ADMIN_PHONE,))
                if not cursor.fetchone():
                    import hashlib
                    password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
                    cursor.execute('''
                        INSERT INTO users (phone, password_hash, created_at, is_admin)
                        VALUES (?, ?, ?, 1)
                    ''', (ADMIN_PHONE, password_hash, datetime.now().isoformat()))
                    conn.commit()
                    print("Администратор создан: login=admin, password=admin123")
        except Exception as e:
            print(f"Error creating admin: {e}")

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def _log_action(self, user_id: int, action: str, details: str):
        """Логирование действий"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_logs (user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, action, details, datetime.now().isoformat()))
        except:
            pass

    # === Пользователи ===
    def create_user(self, phone: str, password: str, is_admin: bool = False) -> Optional[int]:
        """Создание нового пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                password_hash = self._hash_password(password)
                cursor.execute('''
                    INSERT INTO users (phone, password_hash, created_at, is_admin)
                    VALUES (?, ?, ?, ?)
                ''', (phone, password_hash, datetime.now().isoformat(), 1 if is_admin else 0))
                self._log_action(cursor.lastrowid, 'register', 'New user registered')
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def authenticate_user(self, phone: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone = ? AND is_active = 1', (phone,))
            row = cursor.fetchone()
            password_hash = self._hash_password(password)
            if row and row['password_hash'] == password_hash:
                self._log_action(row['id'], 'login', 'User logged in')
                return User(
                    id=row['id'],
                    phone=row['phone'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    is_active=bool(row['is_active']),
                    is_admin=bool(row['is_admin'])
                )
        return None

    def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    phone=row['phone'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    is_active=bool(row['is_active']),
                    is_admin=bool(row['is_admin'])
                )
        return None

    def get_all_users(self) -> List[User]:
        """Получение всех пользователей"""
        users = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            for row in cursor.fetchall():
                users.append(User(
                    id=row['id'],
                    phone=row['phone'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    is_active=bool(row['is_active']),
                    is_admin=bool(row['is_admin'])
                ))
        return users

    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                self._log_action(user_id, 'delete_user', f'User {user_id} deleted')
                return True
        except:
            return False

    def get_system_logs(self, limit: int = 100) -> List[SystemLog]:
        """Получение логов системы"""
        logs = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
            for row in cursor.fetchall():
                logs.append(SystemLog(
                    id=row['id'],
                    user_id=row['user_id'],
                    action=row['action'],
                    details=row['details'],
                    timestamp=row['timestamp']
                ))
        return logs

    # === Профили ===
    def save_profile(self, profile: Profile) -> bool:
        """Сохранение профиля пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO profiles (
                        user_id, full_name, age, gender, occupation, contact_info, photo_path,
                        budget_min, budget_max, preferred_districts, housing_type, rental_period,
                        daily_schedule, cleanliness_level, noise_tolerance, smoking, alcohol,
                        personality_type, hobbies, has_pets, preferred_neighbor_gender,
                        neighbor_age_min, neighbor_age_max, important_criteria
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile.user_id,
                    profile.full_name,
                    profile.age,
                    profile.gender,
                    profile.occupation,
                    profile.contact_info,
                    profile.photo_path,
                    profile.budget_min,
                    profile.budget_max,
                    json.dumps(profile.preferred_districts),
                    profile.housing_type,
                    profile.rental_period,
                    profile.daily_schedule,
                    profile.cleanliness_level,
                    profile.noise_tolerance,
                    1 if profile.smoking else 0,
                    1 if profile.alcohol else 0,
                    profile.personality_type,
                    json.dumps(profile.hobbies),
                    1 if profile.has_pets else 0,
                    profile.preferred_neighbor_gender,
                    profile.neighbor_age_min,
                    profile.neighbor_age_max,
                    json.dumps(profile.important_criteria)
                ))
                self._log_action(profile.user_id, 'save_profile', 'Profile saved')
                return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def get_profile(self, user_id: int) -> Optional[Profile]:
        """Получение профиля пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return Profile(
                    user_id=row['user_id'],
                    full_name=row['full_name'] or "",
                    age=row['age'] or 0,
                    gender=row['gender'] or "",
                    occupation=row['occupation'] or "",
                    contact_info=row['contact_info'] or "",
                    photo_path=row['photo_path'] or "",
                    budget_min=row['budget_min'] or 5000,
                    budget_max=row['budget_max'] or 50000,
                    preferred_districts=json.loads(row['preferred_districts']) if row['preferred_districts'] else [],
                    housing_type=row['housing_type'] or "",
                    rental_period=row['rental_period'] or "",
                    daily_schedule=row['daily_schedule'] or "",
                    cleanliness_level=row['cleanliness_level'] or 5,
                    noise_tolerance=row['noise_tolerance'] or 5,
                    smoking=bool(row['smoking']),
                    alcohol=bool(row['alcohol']),
                    personality_type=row['personality_type'] or 5,
                    hobbies=json.loads(row['hobbies']) if row['hobbies'] else [],
                    has_pets=bool(row['has_pets']),
                    preferred_neighbor_gender=row['preferred_neighbor_gender'] or "",
                    neighbor_age_min=row['neighbor_age_min'] or 18,
                    neighbor_age_max=row['neighbor_age_max'] or 60,
                    important_criteria=json.loads(row['important_criteria']) if row['important_criteria'] else []
                )
        return None

    def get_all_profiles(self, exclude_user_id: int = None) -> List[Profile]:
        """Получение всех профилей"""
        profiles = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_user_id:
                cursor.execute('SELECT * FROM profiles WHERE user_id != ?', (exclude_user_id,))
            else:
                cursor.execute('SELECT * FROM profiles')
            for row in cursor.fetchall():
                profiles.append(Profile(
                    user_id=row['user_id'],
                    full_name=row['full_name'] or "",
                    age=row['age'] or 0,
                    gender=row['gender'] or "",
                    occupation=row['occupation'] or "",
                    contact_info=row['contact_info'] or "",
                    photo_path=row['photo_path'] or "",
                    budget_min=row['budget_min'] or 5000,
                    budget_max=row['budget_max'] or 50000,
                    preferred_districts=json.loads(row['preferred_districts']) if row['preferred_districts'] else [],
                    housing_type=row['housing_type'] or "",
                    rental_period=row['rental_period'] or "",
                    daily_schedule=row['daily_schedule'] or "",
                    cleanliness_level=row['cleanliness_level'] or 5,
                    noise_tolerance=row['noise_tolerance'] or 5,
                    smoking=bool(row['smoking']),
                    alcohol=bool(row['alcohol']),
                    personality_type=row['personality_type'] or 5,
                    hobbies=json.loads(row['hobbies']) if row['hobbies'] else [],
                    has_pets=bool(row['has_pets']),
                    preferred_neighbor_gender=row['preferred_neighbor_gender'] or "",
                    neighbor_age_min=row['neighbor_age_min'] or 18,
                    neighbor_age_max=row['neighbor_age_max'] or 60,
                    important_criteria=json.loads(row['important_criteria']) if row['important_criteria'] else []
                ))
        return profiles

    # === Свайпы ===
    def create_swipe(self, user_id: int, target_user_id: int, direction: str) -> Optional[int]:
        """Создание свайпа"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO swipes (user_id, target_user_id, direction, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, target_user_id, direction, datetime.now().isoformat()))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating swipe: {e}")
            return None

    def get_swipes(self, user_id: int) -> List[Swipe]:
        """Получение свайпов пользователя"""
        swipes = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM swipes WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            for row in cursor.fetchall():
                swipes.append(Swipe(
                    id=row['id'],
                    user_id=row['user_id'],
                    target_user_id=row['target_user_id'],
                    direction=row['direction'],
                    created_at=row['created_at']
                ))
        return swipes

    def check_match(self, user1_id: int, user2_id: int) -> bool:
        """Проверка наличия взаимного лайка"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM swipes
                WHERE (user_id = ? AND target_user_id = ? AND direction = 'right')
                   OR (user_id = ? AND target_user_id = ? AND direction = 'right')
            ''', (user1_id, user2_id, user2_id, user1_id))
            return cursor.fetchone()[0] == 2

    # === Матчи ===
    def create_match(self, user1_id: int, user2_id: int) -> Optional[int]:
        """Создание матча"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO matches (user1_id, user2_id, created_at, is_active)
                    VALUES (?, ?, ?, 1)
                ''', (user1_id, user2_id, datetime.now().isoformat()))
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating match: {e}")
            return None

    def get_matches(self, user_id: int) -> List[Tuple[int, str]]:
        """Получение матчей пользователя"""
        matches = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                    CASE WHEN user1_id = ? THEN user2_id ELSE user1_id END as partner_id,
                    p.full_name
                FROM matches m
                LEFT JOIN profiles p ON p.user_id = partner_id
                WHERE (user1_id = ? OR user2_id = ?) AND is_active = 1
            ''', (user_id, user_id, user_id))
            for row in cursor.fetchall():
                matches.append((row['partner_id'], row['full_name'] or f"User {row['partner_id']}"))
        return matches

    # === Сообщения ===
    def send_message(self, sender_id: int, receiver_id: int, content: str) -> int:
        """Отправка сообщения"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (sender_id, receiver_id, content, datetime.now().isoformat()))
            return cursor.lastrowid

    def get_conversation(self, user1_id: int, user2_id: int) -> List[Message]:
        """Получение переписки между пользователями"""
        messages = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages
                WHERE (sender_id = ? AND receiver_id = ?)
                   OR (sender_id = ? AND receiver_id = ?)
                ORDER BY timestamp ASC
            ''', (user1_id, user2_id, user2_id, user1_id))
            for row in cursor.fetchall():
                messages.append(Message(
                    id=row['id'],
                    sender_id=row['sender_id'],
                    receiver_id=row['receiver_id'],
                    content=row['content'],
                    timestamp=row['timestamp'],
                    is_read=bool(row['is_read'])
                ))
        return messages

    def get_user_contacts(self, user_id: int) -> List[Tuple[int, str]]:
        """Получение списка контактов пользователя"""
        contacts = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Получаем только матчи
            matches = self.get_matches(user_id)
            for contact_id, name in matches:
                contacts.append((contact_id, name))
        return contacts

    # === Совместимость ===
    def save_compatibility_result(self, result: CompatibilityResult):
        """Сохранение результата совместимости"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO compatibility_results
                (user_id, candidate_id, compatibility_score, details, calculated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result.user_id,
                result.candidate_id,
                result.compatibility_score,
                json.dumps(result.details),
                result.calculated_at
            ))

    def get_compatibility_result(self, user_id: int, candidate_id: int) -> Optional[CompatibilityResult]:
        """Получение результата совместимости"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM compatibility_results
                WHERE user_id = ? AND candidate_id = ?
            ''', (user_id, candidate_id))
            row = cursor.fetchone()
            if row:
                return CompatibilityResult(
                    user_id=row['user_id'],
                    candidate_id=row['candidate_id'],
                    compatibility_score=row['compatibility_score'],
                    details=json.loads(row['details']) if row['details'] else {},
                    calculated_at=row['calculated_at']
                )
        return None

    # === Статистика для админа ===
    def get_statistics(self) -> dict:
        """Получение статистики системы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Количество пользователей
            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]

            # Количество профилей
            cursor.execute('SELECT COUNT(*) FROM profiles')
            stats['total_profiles'] = cursor.fetchone()[0]

            # Количество матчей
            cursor.execute('SELECT COUNT(*) FROM matches WHERE is_active = 1')
            stats['total_matches'] = cursor.fetchone()[0]

            # Количество свайпов
            cursor.execute('SELECT COUNT(*) FROM swipes')
            stats['total_swipes'] = cursor.fetchone()[0]

            # Количество сообщений
            cursor.execute('SELECT COUNT(*) FROM messages')
            stats['total_messages'] = cursor.fetchone()[0]

            return stats


# Глобальный экземпляр
db = Database()
