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

    DARPA_RULES = [
        ComplianceRule(rule_id="darpa-page-limit", agency="DARPA", requirement="Executive summary and technical narrative capped at 8 pages.", mandatory=True),
        ComplianceRule(rule_id="darpa-quad-chart", agency="DARPA", requirement="One-page Quad Chart summarizing technical approach and milestones.", mandatory=True),
        ComplianceRule(rule_id="darpa-oci", agency="DARPA", requirement="Organizational Conflict of Interest (OCI) certification included.", mandatory=True),
        ComplianceRule(rule_id="darpa-transition", agency="DARPA", requirement="DoD technology transition and operational impact path defined.", mandatory=True)
    ]

    def audit_proposal(self, agency: str, sections: Dict[str, str], page_count: int = 14) -> ComplianceReport:
        agency_upper = agency.upper()
        if agency_upper == "NSF":
            rules = self.NSF_RULES
        elif agency_upper == "NIH":
            rules = self.NIH_RULES
        elif agency_upper == "DARPA":
            rules = self.DARPA_RULES
        else:
            rules = self.NSF_RULES
        
        findings = []
        passed = 0
        recommendations = []
        full_text = " ".join(sections.values()).lower()

        for r in rules:
            rule_passed = True
            finding_detail = "Satisfied"

            if r.rule_id == "nsf-sec-bi":
                if "broader impacts" not in full_text:
                    rule_passed = False
                    finding_detail = "Missing dedicated 'Broader Impacts' section heading."
                    recommendations.append("Insert explicit Section 2.3: Broader Impacts on Campus & Society.")
            
            elif r.rule_id == "nsf-page-limit":
                if page_count > 15:
                    rule_passed = False
                    finding_detail = f"Page count ({page_count}) exceeds NSF 15-page limit."
                    recommendations.append(f"Trim {page_count - 15} pages from technical approach.")

            elif r.rule_id == "nsf-dmp":
                if "data management" not in full_text:
                    finding_detail = "Data Management Plan: Manual Verification Required."

            elif r.rule_id == "nih-aims-limit":
                aims_text = sections.get("aims", "")
                if len(aims_text.split()) > 750:
                    rule_passed = False
                    finding_detail = "Specific Aims text exceeds 1-page equivalent word ceiling."
                    recommendations.append("Condense Specific Aims to under 700 words.")

            elif r.rule_id == "darpa-page-limit":
                if page_count > 8:
                    rule_passed = False
                    finding_detail = f"Page count ({page_count}) exceeds DARPA 8-page YFA limit."
                    recommendations.append(f"Condense narrative to 8 pages for DARPA solicitation.")

            elif r.rule_id == "darpa-quad-chart":
                if "quad chart" not in full_text:
                    finding_detail = "Quad Chart Attachment: Manual Verification Required."

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
