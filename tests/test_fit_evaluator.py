import ast
from datetime import datetime
from pathlib import Path
from uuid import UUID

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    FitEvaluationResult,
    FitEvaluationStatus,
    UserCapabilityProfile,
)
from app.services.fit_evaluator import FitEvaluator


def _profile(**kwargs: object) -> UserCapabilityProfile:
    defaults = {
        "profile_id": "profile-1",
        "primary_role_focus": "backend_engineer",
        "updated_at": datetime.utcnow(),
    }
    defaults.update(kwargs)
    return UserCapabilityProfile(**defaults)


def _analysis(**kwargs: object) -> AnalysisResult:
    defaults = {
        "analysis_id": "analysis-1",
        "job_posting_id": "job-1",
        "raw_posting_id": "raw-1",
        "content_hash": "hash-1",
        "analysis_status": AnalysisStatus.SUCCESS,
        "analysis_confidence": 0.8,
        "system_type": "control_plane",
        "tier_classification": "tier_2",
        "reasoning_summary": "Test analysis.",
        "analyzed_at": datetime.utcnow(),
    }
    defaults.update(kwargs)
    return AnalysisResult(**defaults)


def test_evaluate_fit_returns_fit_evaluation_result() -> None:
    result = FitEvaluator().evaluate_fit(_profile(), _analysis())

    assert isinstance(result, FitEvaluationResult)
    assert result.profile_id == "profile-1"
    assert result.analysis_id == "analysis-1"
    UUID(result.fit_evaluation_id)


def test_matching_strengths_are_detected() -> None:
    profile = _profile(
        programming_languages=["python"],
        frameworks_and_libraries=["fastapi"],
    )
    analysis = _analysis(
        core_capabilities_required=["python", "fastapi", "kubernetes"],
    )

    result = FitEvaluator().evaluate_fit(profile, analysis)

    assert "python" in result.matching_strengths
    assert "fastapi" in result.matching_strengths
    assert len(result.matching_strengths) == 2


def test_capability_gaps_are_detected() -> None:
    profile = _profile(programming_languages=["python"])
    analysis = _analysis(
        core_capabilities_required=["python", "oauth2", "reporting"],
    )

    result = FitEvaluator().evaluate_fit(profile, analysis)

    assert "oauth2" in result.capability_gaps
    assert "reporting" in result.capability_gaps
    assert "python" not in result.capability_gaps


def test_high_risk_gaps_are_classified() -> None:
    profile = _profile()
    analysis = _analysis(
        core_capabilities_required=["oauth2", "reporting"],
    )

    result = FitEvaluator().evaluate_fit(profile, analysis)

    assert "oauth2" in result.high_risk_gaps
    assert "reporting" in result.low_risk_gaps
    assert "oauth2" not in result.low_risk_gaps


def test_fit_score_is_calculated_correctly() -> None:
    profile = _profile(
        programming_languages=["python"],
        integration_capabilities=["api_integration"],
    )
    analysis = _analysis(
        core_capabilities_required=["python", "api_integration"],
        architecture_signals=["event_driven"],
        business_problem_categories=["crm_workflow"],
    )

    result = FitEvaluator().evaluate_fit(profile, analysis)

    assert result.fit_score == 0.5
    assert result.fit_status == FitEvaluationStatus.SUCCESS
    assert result.confidence == 0.7


def test_empty_job_requirements_returns_warning_with_neutral_score() -> None:
    result = FitEvaluator().evaluate_fit(_profile(), _analysis())

    assert result.fit_status == FitEvaluationStatus.WARNING
    assert result.fit_score == 0.5
    assert result.confidence == 0.4
    assert result.matching_strengths == []
    assert result.capability_gaps == []


def test_no_llm_or_openai_dependency() -> None:
    tree = ast.parse(
        Path("app/services/fit_evaluator.py").read_text(encoding="utf-8")
    )
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("openai" in module for module in imported_modules)
    assert not any("llm_adapter" in module for module in imported_modules)
