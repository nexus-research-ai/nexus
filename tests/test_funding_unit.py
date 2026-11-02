from nexus_funding.finder import FundingFinder

def test_funding_ceiling_parsing():
    finder = FundingFinder()
    opps = finder.list_all("NSF")
    assert len(opps) > 0
    assert "$" in opps[0].award_ceiling
