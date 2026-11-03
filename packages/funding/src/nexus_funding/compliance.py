from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ComplianceRule(BaseModel):
    rule_id: str
    agency: str
    requirement: str
    mandatory: bool = True
    checked: bool = False
    details: str = ""

class ComplianceReport(BaseModel):
    agency: str
    overall_compliance_score: int
    passed_rules: int
    total_rules: int
    ready_for_submission: bool
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)

class SolicitationComplianceChecker:
    """Pre-flight audit engine enforcing federal agency submission guidelines."""

    NSF_RULES = [
        ComplianceRule(rule_id="nsf-sec-bi", agency="NSF", requirement="Broader Impacts must be in a separate, labeled subsection in Project Description.", mandatory=True),
        ComplianceRule(rule_id="nsf-page-limit", agency="NSF", requirement="Technical narrative cannot exceed 15 single-spaced pages.", mandatory=True),
        ComplianceRule(rule_id="nsf-dmp", agency="NSF", requirement="Data Management and Sharing Plan (2 pages) must be attached.", mandatory=True),
        ComplianceRule(rule_id="nsf-citations", agency="NSF", requirement="All factual claims must include peer-reviewed bibliographic citations.", mandatory=True)
    ]

    NIH_RULES = [
        ComplianceRule(rule_id="nih-aims-limit", agency="NIH", requirement="Specific Aims section strictly capped at 1 single-spaced page.", mandatory=True),
        ComplianceRule(rule_id="nih-strategy-limit", agency="NIH", requirement="Research Strategy capped at 6 pages (R21) or 12 pages (R01).", mandatory=True),
        ComplianceRule(rule_id="nih-rigor", agency="NIH", requirement="Scientific Rigor and Prior Research Foundation section required.", mandatory=True),
        ComplianceRule(rule_id="nih-auth", agency="NIH", requirement="Authentication of Key Biological and Chemical Resources included.", mandatory=False)
    ]

    def audit_proposal(self, agency: str, sections: Dict[str, str], page_count: int = 14) -> ComplianceReport:
        agency_upper = agency.upper()
        rules = self.NSF_RULES if agency_upper == "NSF" else self.NIH_RULES
        
        findings = []
        passed = 0
        recommendations = []

        for r in rules:
            rule_passed = True
            finding_detail = "Satisfied"

            if r.rule_id == "nsf-sec-bi":
                text = " ".join(sections.values()).lower()
                if "broader impacts" not in text:
                    rule_passed = False
                    finding_detail = "Missing dedicated 'Broader Impacts' section heading."
                    recommendations.append("Insert explicit Section 2.3: Broader Impacts on Campus & Society.")
            
            elif r.rule_id == "nsf-page-limit":
                if page_count > 15:
                    rule_passed = False
                    finding_detail = f"Page count ({page_count}) exceeds NSF 15-page limit."
                    recommendations.append(f"Trim {page_count - 15} pages from technical approach.")

            elif r.rule_id == "nih-aims-limit":
                aims_text = sections.get("aims", "")
                if len(aims_text.split()) > 750:
                    rule_passed = False
                    finding_detail = "Specific Aims text exceeds 1-page equivalent word ceiling."
                    recommendations.append("Condense Specific Aims to under 700 words.")

            if rule_passed:
                passed += 1
            findings.append({
                "rule_id": r.rule_id,
                "requirement": r.requirement,
                "passed": rule_passed,
                "detail": finding_detail
            })

        score = int((passed / len(rules)) * 100)
        return ComplianceReport(
            agency=agency_upper,
            overall_compliance_score=score,
            passed_rules=passed,
            total_rules=len(rules),
            ready_for_submission=(score >= 90),
            findings=findings,
            actionable_recommendations=recommendations
        )
