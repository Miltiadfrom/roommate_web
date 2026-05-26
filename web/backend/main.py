"""
FastAPI приложение для Roommate Finder
"""
from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from models import User, Profile, Swipe, Match, Message, CompatibilityResult
from database import db
from algorithms import compatibility_calculator
from config import CORS_ORIGINS

app = FastAPI(title="Roommate Finder API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Pydantic модели ===
class UserLogin(BaseModel):
    phone: str
    password: str


class UserRegister(BaseModel):
    phone: str
    password: str


class ProfileUpdate(BaseModel):
    full_name: str = ""
    age: int = 0
    gender: str = ""
    occupation: str = ""
    contact_info: str = ""
    budget_min: int = 5000
    budget_max: int = 50000
    preferred_districts: List[str] = []
    housing_type: str = ""
    rental_period: str = ""
    daily_schedule: str = ""
    cleanliness_level: int = 5
    noise_tolerance: int = 5
    smoking: bool = False
    alcohol: bool = False
    personality_type: int = 5
    hobbies: List[str] = []
    has_pets: bool = False
    preferred_neighbor_gender: str = ""
    neighbor_age_min: int = 18
    neighbor_age_max: int = 60
    important_criteria: List[str] = []


class SwipeRequest(BaseModel):
    target_user_id: int
    direction: str  # 'left', 'right', 'up'


class MessageSend(BaseModel):
    content: str


# === Утилиты ===
async def get_current_user(x_user_id: Optional[str] = Header(None)) -> User:
    """Получение текущего пользователя по user_id из заголовка"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    try:
        user_id = int(x_user_id)
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")


# === Auth endpoints ===
@app.post("/api/auth/register")
async def register(data: UserRegister):
    """Регистрация нового пользователя"""
    user_id = db.create_user(data.phone, data.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Создаем пустой профиль
    profile = Profile(user_id=user_id)
    db.save_profile(profile)
    
    return {"user_id": user_id}


@app.post("/api/auth/login")
async def login(data: UserLogin):
    """Вход пользователя"""
    user = db.authenticate_user(data.phone, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"user_id": user.id}


# === Profile endpoints ===
@app.get("/api/profile/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Получение профиля текущего пользователя"""
    profile = db.get_profile(current_user.id)
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.save_profile(profile)
    return profile.to_dict()


@app.put("/api/profile/me")
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Обновление профиля"""
    profile = db.get_profile(current_user.id)
    if not profile:
        profile = Profile(user_id=current_user.id)
    
    # Обновляем поля
    for field, value in data.model_dump().items():
        setattr(profile, field, value)
    
    db.save_profile(profile)
    return profile.to_dict()


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    """Получение профиля другого пользователя"""
    profile = db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.to_dict()


# === Swipe endpoints ===
@app.post("/api/swipe")
async def create_swipe(
    data: SwipeRequest,
    current_user: User = Depends(get_current_user)
):
    """Создание свайпа"""
    swipe_id = db.create_swipe(current_user.id, data.target_user_id, data.direction)
    
    # Проверяем на матч при лайке
    is_match = False
    if data.direction == "right":
        if db.check_match(current_user.id, data.target_user_id):
            db.create_match(current_user.id, data.target_user_id)
            is_match = True
    
    return {"swipe_id": swipe_id, "is_match": is_match}


@app.get("/api/candidates")
async def get_candidates(current_user: User = Depends(get_current_user)):
    """Получение кандидатов для просмотра"""
    all_profiles = db.get_all_profiles(exclude_user_id=current_user.id)
    
    # Получаем уже просвайпанные
    swiped = {s.target_user_id for s in db.get_swipes(current_user.id)}
    
    # Фильтруем
    candidates = []
    my_profile = db.get_profile(current_user.id)
    
    for profile in all_profiles:
        if profile.user_id not in swiped:
            # Рассчитываем совместимость
            score, details = compatibility_calculator.calculate_compatibility(my_profile, profile)
            candidates.append({
                "profile": profile.to_dict(),
                "compatibility_score": score,
                "compatibility_details": details
            })
    
    # Сортируем по совместимости
    candidates.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    return candidates


# === Match endpoints ===
@app.get("/api/matches")
async def get_matches(current_user: User = Depends(get_current_user)):
    """Получение матчей пользователя"""
    matches = db.get_matches(current_user.id)
    return [{"user_id": uid, "name": name} for uid, name in matches]


# === Message endpoints ===
@app.post("/api/messages/{receiver_id}")
async def send_message(
    receiver_id: int,
    data: MessageSend,
    current_user: User = Depends(get_current_user)
):
    """Отправка сообщения"""
    # Проверяем наличие матча
    matches = db.get_matches(current_user.id)
    match_ids = [uid for uid, _ in matches]
    
    if receiver_id not in match_ids:
        raise HTTPException(status_code=403, detail="Can only message matches")
    
    message_id = db.send_message(current_user.id, receiver_id, data.content)
    return {"message_id": message_id}


@app.get("/api/messages/{other_user_id}")
async def get_conversation(
    other_user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Получение переписки"""
    messages = db.get_conversation(current_user.id, other_user_id)
    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "content": m.content,
        "timestamp": m.timestamp
    } for m in messages]


@app.get("/api/contacts")
async def get_contacts(current_user: User = Depends(get_current_user)):
    """Получение списка контактов"""
    contacts = db.get_user_contacts(current_user.id)
    return [{"user_id": uid, "name": name} for uid, name in contacts]


# === Compatibility endpoints ===
@app.get("/api/compatibility/{candidate_id}")
async def get_compatibility(
    candidate_id: int,
    current_user: User = Depends(get_current_user)
):
    """Расчет совместимости с кандидатом"""
    my_profile = db.get_profile(current_user.id)
    candidate_profile = db.get_profile(candidate_id)
    
    if not candidate_profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    score, details = compatibility_calculator.calculate_compatibility(my_profile, candidate_profile)
    
    # Сохраняем результат
    result = CompatibilityResult(
        user_id=current_user.id,
        candidate_id=candidate_id,
        compatibility_score=score,
        details=details
    )
    db.save_compatibility_result(result)
    
    return {"score": score, "details": details}


# === Admin endpoints ===
@app.get("/api/admin/users/{user_id}/check")
async def check_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Проверка прав администратора"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"is_admin": user.is_admin}


@app.get("/api/admin/statistics")
async def get_statistics(current_user: User = Depends(get_current_user)):
    """Получение статистики (только для админа)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = db.get_statistics()
    return stats


@app.get("/api/admin/users")
async def get_all_users(current_user: User = Depends(get_current_user)):
    """Получение всех пользователей (только для админа)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.get_all_users()
    return [u.to_dict() for u in users]


@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Удаление пользователя (только для админа)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db.delete_user(user_id)
    return {"status": "deleted"}


# === Health check ===
@app.get("/api/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
