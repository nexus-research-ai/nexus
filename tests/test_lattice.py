from nexus_contracts.lattice import Tier, TierLattice, combine_tiers

def test_tier_ordering():
    assert Tier.PUBLIC < Tier.SHARED < Tier.CONFIDENTIAL
    assert Tier.CONFIDENTIAL > Tier.PUBLIC

def test_combine_tiers_max_rule():
    assert combine_tiers(Tier.PUBLIC, Tier.SHARED) == Tier.SHARED
    assert combine_tiers(Tier.PUBLIC, Tier.CONFIDENTIAL) == Tier.CONFIDENTIAL
    assert combine_tiers(Tier.PUBLIC) == Tier.PUBLIC

def test_lattice_flow():
    assert TierLattice.permits_flow(Tier.PUBLIC, Tier.SHARED) is True
    assert TierLattice.permits_flow(Tier.SHARED, Tier.PUBLIC) is False
