"""
Конфигурация приложения для веб-версии
"""
import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'roommate_finder.db')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')

# Создание директорий
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Настройки шифрования
ENCRYPTION_KEY_FILE = os.path.join(DATA_DIR, '.key')

# Настройки приложения
APP_NAME = "Roommate Finder Web"
APP_VERSION = "1.0.0"
MIN_BUDGET = 5000
MAX_BUDGET = 50000

# Настройки совместимости
WEIGHTS = {
    'budget': 0.15,
    'location': 0.15,
    'cleanliness': 0.20,
    'noise': 0.15,
    'schedule': 0.15,
    'habits': 0.10,
    'personality': 0.10
}

# Администратор по умолчанию
ADMIN_PHONE = "admin"
ADMIN_PASSWORD = "admin123"

# Свайп настройки
SWIPE_RIGHT = "right"
SWIPE_LEFT = "left"
SWIPE_UP = "super_like"

# JWT настройки
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 часа

# CORS настройки
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
