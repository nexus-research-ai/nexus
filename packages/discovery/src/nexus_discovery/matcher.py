from typing import Dict, List, Any
from pydantic import BaseModel, Field

class MatchProfile(BaseModel):
    user_id: str
    name: str
    department: str
    academic_role: str
    offers_skills: List[str] = Field(default_factory=list)
    needs_skills: List[str] = Field(default_factory=list)
    available_hours_per_week: int = 10

class MatchResult(BaseModel):
    candidate_id: str
    candidate_name: str
    candidate_department: str
    compatibility_score: int
    match_rationale: str
    they_offer: List[str]
    you_offer: List[str]
    status: str  # proposed, interest_sent, mutual_revealed

class CollaboratorMatcher:
    """Calculates bilateral compatibility scores and manages double opt-in reveals."""

    def evaluate_match(self, user: MatchProfile, candidate: MatchProfile) -> MatchResult:
        # Check mutual skill alignment
        user_offers_candidate_needs = set(user.offers_skills).intersection(set(candidate.needs_skills))
        candidate_offers_user_needs = set(candidate.offers_skills).intersection(set(user.needs_skills))
        
        score = 65
        if user_offers_candidate_needs:
            score += 15
        if candidate_offers_user_needs:
            score += 15
        if user.department != candidate.department:
            score += 4  # Reward interdisciplinary pairings

        score = min(score, 98)
        rationale = f"Strong complementary synergy: {candidate.name} offers expertise in {', '.join(candidate.offers_skills[:2])} matching your proposal requirements."

        return MatchResult(
            candidate_id=candidate.user_id,
            candidate_name=candidate.name,
            candidate_department=candidate.department,
            compatibility_score=score,
            match_rationale=rationale,
            they_offer=candidate.offers_skills,
            you_offer=user.offers_skills,
            status="proposed"
        )
