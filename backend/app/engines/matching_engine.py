"""
Financing Option Matching Engine
Deterministic scheme evaluation against SME financial profile.
NO LLM IMPORTS ALLOWED (TRD DE-01).
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from app.knowledge.scheme_catalog import SchemeCatalog
from app.models.schemas import SchemeEvaluation, FailedRule

class MatchingEngine:
    """Evaluates financing schemes with mathematical precision and explicit 'Why-Not' gap diagnostics."""

    @classmethod
    def evaluate(
        cls,
        dscr: float,
        annual_turnover_bdt: float,
        operating_months: int,
        leverage: float,
        cib_clearance: bool = True,
        is_women_owned: bool = False,
        industry: str = "Retail"
    ) -> List[SchemeEvaluation]:
        schemes = SchemeCatalog.load_all()
        results: List[SchemeEvaluation] = []
        today = date.today()

        for s in schemes:
            rules = s.eligibility_rules
            failed_rules: List[FailedRule] = []
            remediations: List[str] = []

            # 1. CIB clearance check
            if rules.cib_clearance and not cib_clearance:
                failed_rules.append(FailedRule(
                    rule_name="cib_clearance",
                    required="Clean Credit Information Bureau (CIB) record",
                    actual="Adverse/Unresolved default record detected",
                    gap="Requires settlement and CIB clearance certificate"
                ))
                remediations.append("Obtain official CIB clearance certificate from Bangladesh Bank.")

            # 2. DSCR check
            if rules.min_dscr is not None and dscr < rules.min_dscr:
                gap_val = round(rules.min_dscr - dscr, 2)
                failed_rules.append(FailedRule(
                    rule_name="min_dscr",
                    required=f"≥ {rules.min_dscr:.2f}x",
                    actual=f"{dscr:.2f}x",
                    gap=f"{gap_val:.2f}x below minimum threshold"
                ))
                remediations.append(
                    f"Increase operating cash flows or restructure short-term debt to lift DSCR by {gap_val:.2f}x."
                )

            # 3. Minimum turnover check
            if rules.min_turnover_bdt is not None and annual_turnover_bdt < rules.min_turnover_bdt:
                turnover_gap = rules.min_turnover_bdt - annual_turnover_bdt
                failed_rules.append(FailedRule(
                    rule_name="min_turnover_bdt",
                    required=f"≥ {rules.min_turnover_bdt:,.0f} BDT",
                    actual=f"{annual_turnover_bdt:,.0f} BDT",
                    gap=f"{turnover_gap:,.0f} BDT turnover deficit"
                ))
                remediations.append("Consolidate point-of-sale receipts into audited 12-month bank statements.")

            # 4. Operating history check
            if rules.min_operating_months is not None and operating_months < rules.min_operating_months:
                months_gap = rules.min_operating_months - operating_months
                failed_rules.append(FailedRule(
                    rule_name="min_operating_months",
                    required=f"≥ {rules.min_operating_months} months",
                    actual=f"{operating_months} months",
                    gap=f"{months_gap} months operating history missing"
                ))
                remediations.append(f"Requires an additional {months_gap} months of active trade license renewal.")

            # 5. Leverage ceiling check
            if rules.max_leverage is not None and leverage > rules.max_leverage:
                lev_gap = round(leverage - rules.max_leverage, 2)
                failed_rules.append(FailedRule(
                    rule_name="max_leverage",
                    required=f"≤ {rules.max_leverage:.2f}x",
                    actual=f"{leverage:.2f}x",
                    gap=f"{lev_gap:.2f}x above maximum leverage cap"
                ))
                remediations.append("Inject equity or pay down subordinated debt to de-lever balance sheet.")

            # 6. Specific eligibility constraints (e.g. Women Entrepreneur, Industry)
            if rules.ownership_requirement:
                if "women" in rules.ownership_requirement.lower() and not is_women_owned:
                    failed_rules.append(FailedRule(
                        rule_name="ownership_requirement",
                        required="≥ 51% female equity ownership",
                        actual="Non-qualifying shareholding structure",
                        gap="Entity is not women-owned"
                    ))
                    remediations.append("Applicable only to qualified women-led or women-majority owned enterprises.")

            if "agro" in s.id.lower() and "agro" not in industry.lower():
                failed_rules.append(FailedRule(
                    rule_name="industry_sector",
                    required="Agro-processing or agricultural value-addition sector",
                    actual=f"{industry} sector",
                    gap="Industry sector mismatch"
                ))
                remediations.append("Apply under general commercial retail refinance facilities.")

            eligible = (len(failed_rules) == 0)

            # Match score calculation
            if eligible:
                # Lower rate = higher score
                match_score = max(70, min(98, int(100 - (s.rate_cap_pct * 3))))
            else:
                # Penalty based on number of failed rules
                match_score = max(15, 60 - (len(failed_rules) * 15))

            # Check staleness (>180 days since retrieval)
            retrieval_dt = date.fromisoformat(s.retrieval_date)
            is_stale = (today - retrieval_dt).days > 180

            results.append(SchemeEvaluation(
                id=s.id,
                name=s.name,
                issuer=s.issuer,
                rate_pct=s.rate_cap_pct,
                max_amount=s.max_amount_bdt,
                currency="BDT",
                tenure_months=s.tenure_months,
                eligible=eligible,
                match_score=match_score,
                effective_date=s.effective_date,
                source_url=s.source_url,
                is_stale=is_stale,
                status_tag=s.status,
                failed_rules=failed_rules,
                remediation_steps=remediations,
                required_documents=rules.required_documents
            ))

        # Sort: eligible first, then match_score descending
        results.sort(key=lambda x: (not x.eligible, -x.match_score))
        return results
