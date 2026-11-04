from fastapi import APIRouter, Query
from typing import Optional
from nexus_funding.finder import FundingFinder
from nexus_funding.tracker import PursuitTracker

router = APIRouter()
finder = FundingFinder()
tracker = PursuitTracker()

@router.get("/opportunities")
def list_opportunities(agency: Optional[str] = None):
    return {"opportunities": [o.model_dump() for o in finder.list_all(agency)]}

@router.get("/tracker/{proposal_id}")
def get_tracker_state(proposal_id: str, opp_title: str = "NSF Smart & Connected Communities"):
    state = tracker.create_tracker(proposal_id, opp_title)
    return state.model_dump()
