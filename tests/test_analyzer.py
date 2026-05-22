from datetime import datetime
from uuid import UUID

import pytest

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    AnalyzerLLMResult,
    JobPosting,
)
from app.services.analyzer import HybridAnalyzer
from app.services.llm_adapter import LLMAdapterResult


def _job_posting(
    *,
    title: str = "Software Engineer",
    summary: str = "General backend development role.",
) -> JobPosting:
    return JobPosting(
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        source="test",
        title=title,
        summary=summary,
        normalized_at=datetime.utcnow(),
    )


def test_deterministic_analysis_returns_analysis_result() -> None:
    analyzer = HybridAnalyzer()
    result = analyzer.analyze(_job_posting())

    assert isinstance(result, AnalysisResult)
    assert result.analysis_status == AnalysisStatus.SUCCESS
    assert result.analysis_confidence == 0.5
    assert result.system_type == "unknown"
    assert result.tier_classification == "unknown"
    assert result.reasoning_summary == "Deterministic baseline analysis completed."
    UUID(result.analysis_id)


def test_workflow_keyword_sets_system_type() -> None:
    analyzer = HybridAnalyzer()
    result = analyzer.analyze(
        _job_posting(
            title="Automation Engineer",
            summary="Build Zapier workflows for operations.",
        )
    )

    assert result.system_type == "workflow_automation"


def test_ai_keyword_sets_ai_involvement_level() -> None:
    analyzer = HybridAnalyzer()
    result = analyzer.analyze(
        _job_posting(
            title="AI Engineer",
            summary="Integrate OpenAI GPT models into services.",
        )
    )

    assert result.ai_involvement_level == "bounded_ai_step"


class FakeSuccessfulAdapter:
    def analyze_job_posting(self, job_posting: JobPosting) -> LLMAdapterResult:
        return LLMAdapterResult(
            success=True,
            llm_result=AnalyzerLLMResult(
                system_type="control_plane",
                tier_classification="tier_2",
                pipeline_pattern="ingest_normalize_analyze",
                ai_involvement_level="none",
                automation_level="high",
                integration_complexity="medium",
                core_capabilities_required=["python", "fastapi"],
                architecture_signals=["event_driven"],
                business_problem_categories=["ops_automation"],
                hardest_interview_concepts=["idempotency"],
                missing_information=["budget"],
                reasoning_summary="Enriched by fake adapter.",
                llm_confidence=0.92,
            ),
            model_name="fake-model",
        )


def test_fake_successful_adapter_enriches_baseline() -> None:
    analyzer = HybridAnalyzer(
        llm_adapter=FakeSuccessfulAdapter(),
        use_llm=True,
    )
    result = analyzer.analyze(
        _job_posting(
            title="Integration role",
            summary="Connect systems via API and webhook.",
        )
    )

    assert result.analysis_status == AnalysisStatus.SUCCESS
    assert result.system_type == "control_plane"
    assert result.tier_classification == "tier_2"
    assert result.pipeline_pattern == "ingest_normalize_analyze"
    assert result.ai_involvement_level == "none"
    assert result.automation_level == "high"
    assert result.integration_complexity == "medium"
    assert result.reasoning_summary == "Enriched by fake adapter."
    assert result.analysis_confidence == 0.92
    assert "api_integration" in result.architecture_signals
    assert "event_driven" in result.architecture_signals
    assert "ops_automation" in result.business_problem_categories
    assert "python" in result.core_capabilities_required


class FakeFailingAdapter:
    def analyze_job_posting(self, job_posting: JobPosting) -> LLMAdapterResult:
        return LLMAdapterResult(
            success=False,
            error_message="LLM service unavailable",
        )


def test_fake_failing_adapter_returns_warning_without_exception() -> None:
    analyzer = HybridAnalyzer(
        llm_adapter=FakeFailingAdapter(),
        use_llm=True,
    )

    result = analyzer.analyze(_job_posting())

    assert isinstance(result, AnalysisResult)
    assert result.analysis_status == AnalysisStatus.WARNING
    assert result.analysis_confidence == 0.4
    assert "LLM service unavailable" in result.analysis_issues


def test_system_owned_fields_preserved_during_merge() -> None:
    job = _job_posting(
        title="Platform Engineer",
        summary="Maintain control plane services.",
    )
    analyzer = HybridAnalyzer(
        llm_adapter=FakeSuccessfulAdapter(),
        use_llm=True,
    )

    result = analyzer.analyze(job)

    assert result.job_posting_id == "job-1"
    assert result.raw_posting_id == "raw-1"
    assert result.content_hash == "hash-1"
    UUID(result.analysis_id)
    assert result.analyzed_at is not None
