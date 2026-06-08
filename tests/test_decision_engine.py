import ast
from datetime import datetime
from pathlib import Path
from uuid import UUID

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    ApplicationDecision,
    DecisionResult,
    DecisionStatus,
    FitEvaluationResult,
    FitEvaluationStatus,
)
from app.services.decision_engine import DecisionEngine


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


def _fit_evaluation(**kwargs: object) -> FitEvaluationResult:
    defaults = {
        "fit_evaluation_id": "fit-1",
        "analysis_id": "analysis-1",
        "profile_id": "profile-1",
        "fit_status": FitEvaluationStatus.SUCCESS,
        "fit_score": 0.8,
        "confidence": 0.88,
        "evaluation_summary": "Test fit evaluation.",
        "evaluated_at": datetime.utcnow(),
    }
    defaults.update(kwargs)
    return FitEvaluationResult(**defaults)


def test_high_fit_score_with_no_high_risk_gaps_returns_apply() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(
            fit_score=0.82,
            matching_strengths=["python", "fastapi"],
            positioning_advantages=["Strong alignment with api_integration"],
        ),
    )

    assert isinstance(result, DecisionResult)
    assert result.decision == ApplicationDecision.APPLY
    assert result.decision_status == DecisionStatus.SUCCESS
    assert result.decision_confidence == 0.88
    assert "python" in result.supporting_reasons
    UUID(result.decision_id)


def test_moderate_fit_score_returns_maybe() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(
            fit_score=0.55,
            high_risk_gaps=["oauth2"],
            capability_gaps=["oauth2", "reporting"],
        ),
    )

    assert result.decision == ApplicationDecision.MAYBE
    assert result.decision_status == DecisionStatus.WARNING
    assert result.primary_reason == "Moderate fit score requires further evaluation."


def test_low_fit_score_returns_skip() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(fit_score=0.35),
    )

    assert result.decision == ApplicationDecision.SKIP
    assert result.decision_status == DecisionStatus.SUCCESS
    assert result.primary_reason == "Fit score below minimum threshold."


def test_multiple_high_risk_gaps_returns_skip() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(
            fit_score=0.65,
            high_risk_gaps=["oauth2", "kubernetes"],
            positioning_concerns=["High-risk gap: oauth2"],
        ),
    )

    assert result.decision == ApplicationDecision.SKIP
    assert result.primary_reason == "Multiple high-risk capability gaps identified."
    assert "oauth2" in result.blocking_concerns
    assert "kubernetes" in result.blocking_concerns


def test_maybe_includes_follow_up_questions() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(
            fit_score=0.55,
            high_risk_gaps=["oauth2"],
        ),
    )

    assert result.decision == ApplicationDecision.MAYBE
    assert len(result.follow_up_questions) > 0
    assert "oauth2" in result.follow_up_questions[0]


def test_apply_includes_proposal_prep_next_steps() -> None:
    result = DecisionEngine().decide(
        _analysis(),
        _fit_evaluation(fit_score=0.9),
    )

    assert result.decision == ApplicationDecision.APPLY
    assert any("proposal" in step.lower() for step in result.recommended_next_steps)
    assert any("prep" in step.lower() or "prepare" in step.lower()
               for step in result.recommended_next_steps)


def test_decision_engine_does_not_import_openai_or_llm_modules() -> None:
    tree = ast.parse(
        Path("app/services/decision_engine.py").read_text(encoding="utf-8")
    )
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
        elif isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)

    assert not any("openai" in module for module in imported_modules)
    assert not any("llm_adapter" in module for module in imported_modules)
