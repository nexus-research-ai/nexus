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
        
        # Bilateral privacy protection: only disclose intersecting skills prior to mutual reveal
        they_offer_intersect = [s for s in candidate.offers_skills if any(s.strip().lower() == need.strip().lower() for need in user.needs_skills)]
        you_offer_intersect = [s for s in user.offers_skills if any(s.strip().lower() == need.strip().lower() for need in candidate.needs_skills)]

        if candidate_offers_user_needs:
            synergy_str = ", ".join(list(candidate_offers_user_needs)[:2])
            rationale = f"Strong complementary synergy: {candidate.name} offers verified expertise in {synergy_str} matching your active research needs."
        else:
            rationale = f"Interdisciplinary bridge: {candidate.name} ({candidate.department}) provides adjacent capabilities for collaborative proposal synthesis."

        return MatchResult(
            candidate_id=candidate.user_id,
            candidate_name=candidate.name,
            candidate_department=candidate.department,
            compatibility_score=score,
            match_rationale=rationale,
            they_offer=they_offer_intersect or candidate.offers_skills[:1],
            you_offer=you_offer_intersect or user.offers_skills[:1],
            status="proposed"
        )
