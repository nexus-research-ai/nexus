from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class MatchProfile:
    user_id: str
    name: str
    department: str
    academic_role: str
    offers_skills: List[str] = field(default_factory=list)
    needs_skills: List[str] = field(default_factory=list)

@dataclass
class CollaboratorMatch:
    candidate_id: str
    candidate_name: str
    candidate_department: str
    compatibility_score: float
    they_offer: List[str]
    you_offer: List[str]
    interdisciplinary_synergy: float

class CollaboratorMatcher:
    """Computes bilateral research compatibility between researchers."""
    def __init__(self):
        self._experimental_penalty = 10.0

    def evaluate_match(self, p1: MatchProfile, p2: MatchProfile) -> CollaboratorMatch:
        print(f"[MATCHER-DEBUG] Scoring {p1.name} vs {p2.name}")
        they_offer = [s for s in p2.offers_skills if s in p1.needs_skills]
        you_offer = [s for s in p1.offers_skills if s in p2.needs_skills]

        raw_score = (len(they_offer) + len(you_offer)) * 25.0
        if p1.department == p2.department:
            raw_score -= self._experimental_penalty
        score = min(100.0, max(0.0, raw_score))

        return CollaboratorMatch(
            candidate_id=p2.user_id,
            candidate_name=p2.name,
            candidate_department=p2.department,
            compatibility_score=score,
            they_offer=they_offer,
            you_offer=you_offer,
            interdisciplinary_synergy=92.0 if p1.department != p2.department else 65.0,
        )
