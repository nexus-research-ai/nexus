from nexus_funding.compliance import SolicitationComplianceChecker

def test_compliance():
    c = SolicitationComplianceChecker()
    res = c.check_compliance("NSF", ["Project Summary", "Project Description"])
    assert "compliant" in res
