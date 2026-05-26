"""
Алгоритмы расчета совместимости для веб-версии
"""
from typing import Dict, List, Tuple
from models import Profile
from config import WEIGHTS


class CompatibilityCalculator:
    def __init__(self):
        self.weights = WEIGHTS

    def calculate_compatibility(self, profile1: Profile, profile2: Profile) -> Tuple[float, Dict]:
        """
        Расчет совместимости между двумя профилями
        Возвращает: (процент совместимости, детали по категориям)
        """
        scores = {}
        total_weight = 0

        # 1. Бюджет (15%)
        budget_score = self._calculate_budget_compatibility(profile1, profile2)
        scores['budget'] = budget_score
        total_weight += self.weights['budget']

        # 2. Район (15%)
        location_score = self._calculate_location_compatibility(profile1, profile2)
        scores['location'] = location_score
        total_weight += self.weights['location']

        # 3. Чистота (20%)
        cleanliness_score = self._calculate_cleanliness_compatibility(profile1, profile2)
        scores['cleanliness'] = cleanliness_score
        total_weight += self.weights['cleanliness']

        # 4. Шум (15%)
        noise_score = self._calculate_noise_compatibility(profile1, profile2)
        scores['noise'] = noise_score
        total_weight += self.weights['noise']

        # 5. Распорядок дня (15%)
        schedule_score = self._calculate_schedule_compatibility(profile1, profile2)
        scores['schedule'] = schedule_score
        total_weight += self.weights['schedule']

        # 6. Привычки (10%)
        habits_score = self._calculate_habits_compatibility(profile1, profile2)
        scores['habits'] = habits_score
        total_weight += self.weights['habits']

        # 7. Личность (10%)
        personality_score = self._calculate_personality_compatibility(profile1, profile2)
        scores['personality'] = personality_score
        total_weight += self.weights['personality']

        # Расчет взвешенного среднего
        weighted_score = (
                scores['budget'] * self.weights['budget'] +
                scores['location'] * self.weights['location'] +
                scores['cleanliness'] * self.weights['cleanliness'] +
                scores['noise'] * self.weights['noise'] +
                scores['schedule'] * self.weights['schedule'] +
                scores['habits'] * self.weights['habits'] +
                scores['personality'] * self.weights['personality']
        )

        # Нормализация к 100%
        final_score = min(100, max(0, weighted_score / total_weight * 100))

        details = {
            'budget': round(scores['budget'] * 100, 1),
            'location': round(scores['location'] * 100, 1),
            'cleanliness': round(scores['cleanliness'] * 100, 1),
            'noise': round(scores['noise'] * 100, 1),
            'schedule': round(scores['schedule'] * 100, 1),
            'habits': round(scores['habits'] * 100, 1),
            'personality': round(scores['personality'] * 100, 1)
        }

        return round(final_score, 1), details

    def _calculate_budget_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по бюджету"""
        # Проверка перекрытия диапазонов бюджета
        min_budget = max(p1.budget_min, p2.budget_min)
        max_budget = min(p1.budget_max, p2.budget_max)

        if min_budget > max_budget:
            return 0.0

        overlap = max_budget - min_budget
        total_range = max(p1.budget_max, p2.budget_max) - min(p1.budget_min, p2.budget_min)

        if total_range == 0:
            return 1.0

        return min(1.0, overlap / total_range)

    def _calculate_location_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по району"""
        if not p1.preferred_districts or not p2.preferred_districts:
            return 0.5

        common_districts = set(p1.preferred_districts) & set(p2.preferred_districts)
        total_districts = set(p1.preferred_districts) | set(p2.preferred_districts)

        if not total_districts:
            return 0.5

        return len(common_districts) / len(total_districts)

    def _calculate_cleanliness_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по чистоте"""
        diff = abs(p1.cleanliness_level - p2.cleanliness_level)
        return max(0, 1.0 - (diff / 10))

    def _calculate_noise_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по отношению к шуму"""
        diff = abs(p1.noise_tolerance - p2.noise_tolerance)
        return max(0, 1.0 - (diff / 10))

    def _calculate_schedule_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по распорядку дня"""
        if p1.daily_schedule == p2.daily_schedule:
            return 1.0
        elif not p1.daily_schedule or not p2.daily_schedule:
            return 0.5
        else:
            # Частичная совместимость (утро-день, день-вечер)
            schedule_order = ['утро', 'день', 'ночь']
            try:
                idx1 = schedule_order.index(p1.daily_schedule)
                idx2 = schedule_order.index(p2.daily_schedule)
                if abs(idx1 - idx2) == 1:
                    return 0.7
                else:
                    return 0.3
            except ValueError:
                return 0.5

    def _calculate_habits_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по привычкам"""
        score = 1.0

        # Курение
        if p1.smoking != p2.smoking:
            score -= 0.5

        # Алкоголь
        if p1.alcohol != p2.alcohol:
            score -= 0.3

        # Животные
        if p1.has_pets != p2.has_pets:
            score -= 0.2

        return max(0, score)

    def _calculate_personality_compatibility(self, p1: Profile, p2: Profile) -> float:
        """Совместимость по личностным характеристикам"""
        diff = abs(p1.personality_type - p2.personality_type)
        return max(0, 1.0 - (diff / 10))

    def filter_profiles(self, profiles: List[Profile], user_profile: Profile) -> List[Profile]:
        """Фильтрация профилей по базовым критериям"""
        filtered = []
        for profile in profiles:
            # Проверка пола
            if user_profile.preferred_neighbor_gender and profile.gender:
                if user_profile.preferred_neighbor_gender != profile.gender:
                    continue

            # Проверка возраста
            if profile.age < user_profile.neighbor_age_min or profile.age > user_profile.neighbor_age_max:
                continue

            # Проверка бюджета (перекрытие)
            if profile.budget_min > user_profile.budget_max or profile.budget_max < user_profile.budget_min:
                continue

            filtered.append(profile)

        return filtered


# Глобальный экземпляр
compatibility_calculator = CompatibilityCalculator()
