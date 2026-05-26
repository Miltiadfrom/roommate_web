"""
Модели данных для веб-версии
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class User:
    id: int
    phone: str
    password_hash: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True
    is_admin: bool = False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'phone': self.phone,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }


@dataclass
class Profile:
    user_id: int
    # Личная информация
    full_name: str = ""
    age: int = 0
    gender: str = ""
    occupation: str = ""
    contact_info: str = ""
    photo_path: str = ""

    # Предпочтения по жилью
    budget_min: int = 5000
    budget_max: int = 50000
    preferred_districts: List[str] = field(default_factory=list)
    housing_type: str = ""
    rental_period: str = ""

    # Привычки и образ жизни
    daily_schedule: str = ""
    cleanliness_level: int = 5
    noise_tolerance: int = 5
    smoking: bool = False
    alcohol: bool = False

    # Личностные характеристики
    personality_type: int = 5
    hobbies: List[str] = field(default_factory=list)
    has_pets: bool = False

    # Требования к соседям
    preferred_neighbor_gender: str = ""
    neighbor_age_min: int = 18
    neighbor_age_max: int = 60
    important_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        return cls(**data)


@dataclass
class Swipe:
    id: int
    user_id: int
    target_user_id: int
    direction: str  # 'left', 'right', 'up'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Match:
    id: int
    user1_id: int
    user2_id: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class Advertisement:
    id: int
    user_id: int
    title: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


@dataclass
class Message:
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    is_read: bool = False


@dataclass
class CompatibilityResult:
    user_id: int
    candidate_id: int
    compatibility_score: float
    details: dict = field(default_factory=dict)
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SystemLog:
    id: int
    user_id: int
    action: str
    details: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
