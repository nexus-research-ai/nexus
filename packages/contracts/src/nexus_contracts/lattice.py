from enum import Enum
from typing import Set, Tuple, List, Optional

class Tier(str, Enum):
    """Security classifications for the Nexus platform."""
    PUBLIC = "PUBLIC"
    SHARED = "SHARED"
    CONFIDENTIAL = "CONFIDENTIAL"

# Initial manual level lookups
_ORDER_MAP = {
    "PUBLIC": 0,
    "SHARED": 1,
    "CONFIDENTIAL": 2,
}

def is_strictly_higher(t1: str, t2: str) -> bool:
    return _ORDER_MAP.get(t1, 0) > _ORDER_MAP.get(t2, 0)

def is_equal_or_higher(t1: str, t2: str) -> bool:
    return _ORDER_MAP.get(t1, 0) >= _ORDER_MAP.get(t2, 0)
