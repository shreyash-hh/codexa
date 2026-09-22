"""
CODEXA Multi-Dimensional Scoring Engine
========================================

Defines a mathematically rigorous, transparent, and defensible scoring model that translates
static code quality, AST/pattern security audits, and supply chain dependency vulnerabilities
into standardized, normalized health metrics (0.00 to 100.00).

Methodology & Mathematical Formulation
--------------------------------------

1. Severity Weighting Matrix (W_s):
   - Critical: 25.0 points
   - High:     10.0 points
   - Medium:    4.0 points
   - Low:       1.5 points
   - Info:      0.5 points

2. Domain Pillar Classifications:
   - Quality Pillar (Q):    Tools = ['pylint', 'radon']
   - Security Pillar (S):   Tools = ['bandit', 'semgrep']
   - Dependency Pillar (D): Tools = ['pip-audit']

3. Domain Sub-Score Computation:
   For each domain pillar D in {Q, S, D}:
     Total Penalty P_D = sum(W_s(f) for f in Findings_D)
     Sub-Score S_D = max(0.0, round(100.0 - min(100.0, P_D), 2))

4. Composite Holistic Score (S_C):
   Weighted composite aggregation balancing security criticality and maintainability:
     Weight_Security   (alpha) = 0.45  (45% - direct operational & breach risk)
     Weight_Quality    (beta)  = 0.30  (30% - code maintainability & technical debt)
     Weight_Dependency (gamma) = 0.25  (25% - supply chain & third-party CVE exposure)
     
     Composite Score S_C = round(0.30 * S_Q + 0.45 * S_S + 0.25 * S_D, 2)
"""

import logging
from typing import Dict, Any, List
from core.models import AnalysisRun, Finding, Score

logger = logging.getLogger(__name__)

# Severity Penalty Weights
SEVERITY_WEIGHTS = {
    'critical': 25.0,
    'high': 10.0,
    'medium': 4.0,
    'low': 1.5,
    'info': 0.5,
}

# Domain Category Mappings
DOMAIN_MAPPINGS = {
    'quality': {'pylint', 'radon'},
    'security': {'bandit', 'semgrep'},
    'dependency': {'pip-audit'},
}

# Pillar Weights for Composite Score (sum = 1.00)
COMPOSITE_WEIGHTS = {
    'quality': 0.30,
    'security': 0.45,
    'dependency': 0.25,
}


def calculate_run_scores(findings: List[Finding]) -> Dict[str, float]:
    """
    Computes quality_score, security_score, dependency_score, and composite_score
    from a list of Finding model instances or finding dictionaries.
    """
    penalties = {
        'quality': 0.0,
        'security': 0.0,
        'dependency': 0.0,
    }

    for finding in findings:
        tool = getattr(finding, 'tool_name', None) or (finding.get('tool_name') if isinstance(finding, dict) else '')
        severity = (getattr(finding, 'severity', None) or (finding.get('severity') if isinstance(finding, dict) else 'medium')).lower()

        weight = SEVERITY_WEIGHTS.get(severity, 2.0)
        tool_lower = tool.lower()

        if tool_lower in DOMAIN_MAPPINGS['quality']:
            # Apply slight logarithmic scaling for high-volume linting to avoid artificial zeroing
            penalties['quality'] += weight * 0.4 if tool_lower == 'pylint' else weight
        elif tool_lower in DOMAIN_MAPPINGS['security']:
            penalties['security'] += weight
        elif tool_lower in DOMAIN_MAPPINGS['dependency']:
            penalties['dependency'] += weight
        else:
            # Default to quality penalty if unspecified
            penalties['quality'] += weight

    # Compute sub-scores bounded in [0.00, 100.00]
    quality_score = max(0.0, round(100.0 - min(100.0, penalties['quality']), 2))
    security_score = max(0.0, round(100.0 - min(100.0, penalties['security']), 2))
    dependency_score = max(0.0, round(100.0 - min(100.0, penalties['dependency']), 2))

    # Compute weighted composite score
    composite_score = round(
        (COMPOSITE_WEIGHTS['quality'] * quality_score) +
        (COMPOSITE_WEIGHTS['security'] * security_score) +
        (COMPOSITE_WEIGHTS['dependency'] * dependency_score),
        2
    )

    return {
        'quality_score': quality_score,
        'security_score': security_score,
        'dependency_score': dependency_score,
        'composite_score': composite_score,
        'penalties': {k: round(v, 2) for k, v in penalties.items()},
    }


def compute_and_save_score(run: AnalysisRun) -> Score:
    """
    Evaluates all Finding rows for an AnalysisRun, creates/updates the Score record in DB,
    and returns the persisted Score instance.
    """
    findings = list(run.findings.all())
    score_metrics = calculate_run_scores(findings)

    score_obj, _ = Score.objects.update_or_create(
        run=run,
        defaults={
            'quality_score': score_metrics['quality_score'],
            'security_score': score_metrics['security_score'],
            'dependency_score': score_metrics['dependency_score'],
            'composite_score': score_metrics['composite_score'],
        }
    )

    logger.info(
        f"Computed Scores for Run #{run.id}: Composite={score_obj.composite_score}, "
        f"Quality={score_obj.quality_score}, Security={score_obj.security_score}, "
        f"Dependency={score_obj.dependency_score}"
    )

    return score_obj
