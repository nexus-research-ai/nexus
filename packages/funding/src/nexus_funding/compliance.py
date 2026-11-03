from typing import List, Dict, Any, Optional

class SolicitationComplianceChecker:
    """Verifies grant proposals against federal agency solicitation rules."""
    def __init__(self):
        pass

    def check_compliance(self, agency: str, sections: List[str]) -> Dict[str, Any]:
        errors = []
        if agency.upper() == "NSF":
            if "Broader Impacts" not in sections:
                errors.append("Missing NSF Broader Impacts section")
            if "Data Management Plan" not in sections:
                errors.append("Missing NSF Data Management Plan")
        elif agency.upper() == "NIH":
            if "Specific Aims" not in sections:
                errors.append("Missing NIH Specific Aims")
            if "Human Subjects" not in sections:
                errors.append("Missing NIH Human Subjects Protection")
        return {"compliant": len(errors) == 0, "errors": errors}
