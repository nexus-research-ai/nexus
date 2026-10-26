from enum import Enum
from typing import Set, Tuple, List, Optional

class Tier(str, Enum):
    """
    Security classifications for the Nexus platform.
    PUBLIC: Openly accessible across campus.
    SHARED: Accessible under authenticated mutual project/pod boundary.
    CONFIDENTIAL: Private to researcher vault, strictly zero-knowledge.
    """
    PUBLIC = "PUBLIC"
    SHARED = "SHARED"
    CONFIDENTIAL = "CONFIDENTIAL"

    def __lt__(self, other):
        if not isinstance(other, Tier):
            return NotImplemented
        order = {Tier.PUBLIC: 0, Tier.SHARED: 1, Tier.CONFIDENTIAL: 2}
        return order[self] < order[other]

    def __le__(self, other):
        if not isinstance(other, Tier):
            return NotImplemented
        order = {Tier.PUBLIC: 0, Tier.SHARED: 1, Tier.CONFIDENTIAL: 2}
        return order[self] <= order[other]

    def __gt__(self, other):
        if not isinstance(other, Tier):
            return NotImplemented
        order = {Tier.PUBLIC: 0, Tier.SHARED: 1, Tier.CONFIDENTIAL: 2}
        return order[self] > order[other]

    def __ge__(self, other):
        if not isinstance(other, Tier):
            return NotImplemented
        order = {Tier.PUBLIC: 0, Tier.SHARED: 1, Tier.CONFIDENTIAL: 2}
        return order[self] >= order[other]

def combine_tiers(*tiers: Tier) -> Tier:
    """Combines multiple tiers using the MAX rule (least upper bound)."""
    if not tiers:
        return Tier.PUBLIC
    max_tier = Tier.PUBLIC
    for t in tiers:
        if t > max_tier:
            max_tier = t
    return max_tier

class TierLattice:
    """Information Flow Control lattice implementation."""
    @staticmethod
    def permits_flow(source_tier: Tier, target_tier: Tier) -> bool:
        return source_tier <= target_tier
