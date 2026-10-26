from enum import Enum
from typing import Sequence

class Tier(str, Enum):
    PUBLIC = "public"
    SHARED = "shared"
    CONFIDENTIAL = "confidential"

    @property
    def level(self) -> int:
        if self == Tier.PUBLIC:
            return 1
        elif self == Tier.SHARED:
            return 2
        return 3

    def __lt__(self, other: "Tier") -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.level < other.level

    def __le__(self, other: "Tier") -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.level <= other.level

    def __gt__(self, other: "Tier") -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.level > other.level

    def __ge__(self, other: "Tier") -> bool:
        if not isinstance(other, Tier):
            return NotImplemented
        return self.level >= other.level


def combine_tiers(*tiers: Tier) -> Tier:
    """Apply the MAX-rule: combining data of tier A and tier B yields max(tier_a, tier_b)."""
    if not tiers:
        return Tier.PUBLIC
    return max(tiers, key=lambda t: t.level)


class TierLattice:
    """Formally-specified 3-tier lattice (PUBLIC < SHARED < CONFIDENTIAL)."""
    LATTICE_VERSION: str = "v1.0"

    @classmethod
    def validate_dominance(cls, high: Tier, low: Tier) -> bool:
        """Verify that high dominates or equals low."""
        return high >= low

    @classmethod
    def permits_flow(cls, source_tier: Tier, sink_tier: Tier) -> bool:
        """Information may flow from low security to high security (no read up, no write down)."""
        return source_tier <= sink_tier
