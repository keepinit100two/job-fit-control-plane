from datetime import datetime

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    AnalyzerLLMResult,
    JobPosting,
    NormalizationResult,
    NormalizationStatus,
    NormalizedJobPostingEnvelope,
    RawJobPosting,
)


def test_raw_job_posting_instantiates_successfully() -> None:
    posting = RawJobPosting(
        raw_posting_id="raw-1",
        source="linkedin",
        source_url="https://example.com/jobs/1",
        capture_method="crawler",
        raw_title="Senior Python Engineer",
        raw_company_name="Example Corp",
        raw_location="Remote",
        raw_text="We are hiring a Senior Python Engineer...",
        captured_at=datetime.utcnow(),
        content_hash="hash-raw-1",
    )

    assert posting.raw_posting_id == "raw-1"
    assert posting.source == "linkedin"


def test_job_posting_instantiates_with_minimal_required_fields() -> None:
    posting = JobPosting(
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-job-1",
        source="linkedin",
        title="Senior Python Engineer",
        summary="Build and maintain backend services.",
        normalized_at=datetime.utcnow(),
    )

    assert posting.job_posting_id == "job-1"
    assert posting.responsibilities == []
    assert posting.required_skills == []


def test_normalization_result_instantiates_with_success_status() -> None:
    result = NormalizationResult(
        raw_posting_id="raw-1",
        content_hash="hash-raw-1",
        status=NormalizationStatus.SUCCESS,
        confidence=0.92,
        raw_text_quality_score=0.88,
        used_llm=True,
        model_name="gpt-4o-mini",
        normalized_at=datetime.utcnow(),
    )

    assert result.status == NormalizationStatus.SUCCESS
    assert result.issues == []
    assert result.missing_required_fields == []


def test_envelope_allows_none_job_posting_on_failure_status() -> None:
    result = NormalizationResult(
        raw_posting_id="raw-2",
        content_hash="hash-raw-2",
        status=NormalizationStatus.FAILURE,
        confidence=0.1,
        raw_text_quality_score=0.2,
        used_llm=False,
        normalized_at=datetime.utcnow(),
    )
    envelope = NormalizedJobPostingEnvelope(
        job_posting=None,
        normalization_result=result,
    )

    assert envelope.job_posting is None
    assert envelope.normalization_result.status == NormalizationStatus.FAILURE


def test_analysis_result_instantiates_successfully() -> None:
    result = AnalysisResult(
        analysis_id="analysis-1",
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        analysis_status=AnalysisStatus.SUCCESS,
        analysis_confidence=0.85,
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Deterministic schema fixture.",
        analyzed_at=datetime.utcnow(),
    )

    assert result.analysis_id == "analysis-1"
    assert result.analysis_issues == []
    assert result.core_capabilities_required == []


def test_analysis_status_enum_values() -> None:
    assert AnalysisStatus.SUCCESS == "success"
    assert AnalysisStatus.WARNING == "warning"
    assert AnalysisStatus.FAILURE == "failure"
    assert AnalysisStatus("warning") is AnalysisStatus.WARNING


def test_analysis_result_list_defaults_are_isolated_per_instance() -> None:
    first = AnalysisResult(
        analysis_id="analysis-1",
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        analysis_status=AnalysisStatus.SUCCESS,
        analysis_confidence=0.8,
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="First instance.",
        analyzed_at=datetime.utcnow(),
    )
    second = AnalysisResult(
        analysis_id="analysis-2",
        job_posting_id="job-2",
        raw_posting_id="raw-2",
        content_hash="hash-2",
        analysis_status=AnalysisStatus.SUCCESS,
        analysis_confidence=0.8,
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Second instance.",
        analyzed_at=datetime.utcnow(),
    )

    first.analysis_issues.append("issue-a")
    first.core_capabilities_required.append("capability-a")

    assert second.analysis_issues == []
    assert second.core_capabilities_required == []


def test_analyzer_llm_result_instantiates_successfully() -> None:
    result = AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="LLM schema fixture.",
        llm_confidence=0.91,
    )

    assert result.system_type == "control_plane"
    assert result.warnings == []
    assert result.core_capabilities_required == []


def test_analyzer_llm_result_list_defaults_are_isolated_per_instance() -> None:
    first = AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="First LLM result.",
        llm_confidence=0.9,
    )
    second = AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Second LLM result.",
        llm_confidence=0.9,
    )

    first.warnings.append("warning-a")
    first.architecture_signals.append("signal-a")

    assert second.warnings == []
    assert second.architecture_signals == []


def test_llm_confidence_is_separate_from_analysis_confidence() -> None:
    llm_result = AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="LLM output.",
        llm_confidence=0.91,
    )
    analysis_result = AnalysisResult(
        analysis_id="analysis-1",
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        analysis_status=AnalysisStatus.SUCCESS,
        analysis_confidence=0.55,
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Merged analysis output.",
        analyzed_at=datetime.utcnow(),
    )

    assert llm_result.llm_confidence == 0.91
    assert analysis_result.analysis_confidence == 0.55
    assert not hasattr(llm_result, "analysis_confidence")
    assert not hasattr(analysis_result, "llm_confidence")
