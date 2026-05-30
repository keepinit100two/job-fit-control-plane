from datetime import datetime

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    AnalyzerLLMResult,
    JobPipelineResult,
    JobPosting,
    NormalizationResult,
    NormalizationStatus,
    NormalizedJobPostingEnvelope,
    RawJobPosting,
    FitEvaluationResult,
    FitEvaluationStatus,
    UserCapabilityProfile,
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


def _normalized_envelope() -> NormalizedJobPostingEnvelope:
    normalization_result = NormalizationResult(
        raw_posting_id="raw-1",
        content_hash="hash-raw-1",
        status=NormalizationStatus.SUCCESS,
        confidence=0.92,
        raw_text_quality_score=0.88,
        used_llm=False,
        normalized_at=datetime.utcnow(),
    )
    job_posting = JobPosting(
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-job-1",
        source="linkedin",
        title="Senior Python Engineer",
        summary="Build and maintain backend services.",
        normalized_at=datetime.utcnow(),
    )
    return NormalizedJobPostingEnvelope(
        job_posting=job_posting,
        normalization_result=normalization_result,
    )


def _analysis_fixture() -> AnalysisResult:
    return AnalysisResult(
        analysis_id="analysis-1",
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-job-1",
        analysis_status=AnalysisStatus.SUCCESS,
        analysis_confidence=0.85,
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Pipeline analysis fixture.",
        analyzed_at=datetime.utcnow(),
    )


def test_job_pipeline_result_with_normalized_only() -> None:
    envelope = _normalized_envelope()
    pipeline_result = JobPipelineResult(normalized=envelope)

    assert pipeline_result.analysis_result is None
    assert pipeline_result.fit_evaluation_result is None
    assert pipeline_result.normalized is envelope


def test_job_pipeline_result_with_normalized_and_analysis() -> None:
    envelope = _normalized_envelope()
    analysis = _analysis_fixture()
    pipeline_result = JobPipelineResult(
        normalized=envelope,
        analysis_result=analysis,
    )

    assert pipeline_result.analysis_result is analysis
    assert pipeline_result.analysis_result.analysis_id == "analysis-1"
    assert pipeline_result.fit_evaluation_result is None


def test_job_pipeline_result_with_normalized_analysis_and_fit_evaluation() -> None:
    envelope = _normalized_envelope()
    analysis = _analysis_fixture()
    fit_evaluation = FitEvaluationResult(
        fit_evaluation_id="fit-1",
        analysis_id="analysis-1",
        profile_id="profile-1",
        fit_status=FitEvaluationStatus.SUCCESS,
        fit_score=0.82,
        confidence=0.88,
        evaluation_summary="Strong alignment with role requirements.",
        evaluated_at=datetime.utcnow(),
    )
    pipeline_result = JobPipelineResult(
        normalized=envelope,
        analysis_result=analysis,
        fit_evaluation_result=fit_evaluation,
    )

    assert pipeline_result.analysis_result is analysis
    assert pipeline_result.fit_evaluation_result is fit_evaluation
    assert pipeline_result.fit_evaluation_result.fit_evaluation_id == "fit-1"


def test_job_pipeline_result_preserves_nested_envelope() -> None:
    envelope = _normalized_envelope()
    pipeline_result = JobPipelineResult(normalized=envelope)

    assert pipeline_result.normalized.job_posting is not None
    assert pipeline_result.normalized.job_posting.job_posting_id == "job-1"
    assert (
        pipeline_result.normalized.normalization_result.status
        == NormalizationStatus.SUCCESS
    )


def test_user_capability_profile_instantiates_successfully() -> None:
    profile = UserCapabilityProfile(
        profile_id="profile-1",
        primary_role_focus="backend_engineer",
        updated_at=datetime.utcnow(),
    )

    assert profile.profile_id == "profile-1"
    assert profile.primary_role_focus == "backend_engineer"
    assert profile.programming_languages == []
    assert profile.strongest_capabilities == []


def test_user_capability_profile_list_defaults_are_isolated_per_instance() -> None:
    first = UserCapabilityProfile(
        profile_id="profile-1",
        primary_role_focus="backend_engineer",
        updated_at=datetime.utcnow(),
    )
    second = UserCapabilityProfile(
        profile_id="profile-2",
        primary_role_focus="platform_engineer",
        updated_at=datetime.utcnow(),
    )

    first.programming_languages.append("python")
    first.ai_capabilities.append("llm_integration")

    assert second.programming_languages == []
    assert second.ai_capabilities == []


def test_user_capability_profile_represents_ai_automation_and_control_plane() -> None:
    profile = UserCapabilityProfile(
        profile_id="profile-1",
        primary_role_focus="control_plane_engineer",
        programming_languages=["python"],
        frameworks_and_libraries=["fastapi", "pydantic"],
        ai_capabilities=["openai_structured_outputs", "prompt_design"],
        automation_capabilities=["workflow_orchestration", "zapier"],
        architecture_patterns=["event_driven", "idempotent_ingest"],
        strongest_capabilities=["pipeline_design", "schema_modeling"],
        preferred_work_types=["control_plane", "workflow_automation"],
        updated_at=datetime.utcnow(),
    )

    assert profile.primary_role_focus == "control_plane_engineer"
    assert "openai_structured_outputs" in profile.ai_capabilities
    assert "workflow_orchestration" in profile.automation_capabilities
    assert "control_plane" in profile.preferred_work_types


def test_fit_evaluation_result_instantiates_successfully() -> None:
    result = FitEvaluationResult(
        fit_evaluation_id="fit-1",
        analysis_id="analysis-1",
        profile_id="profile-1",
        fit_status=FitEvaluationStatus.SUCCESS,
        fit_score=0.82,
        confidence=0.88,
        evaluation_summary="Strong alignment with control-plane requirements.",
        evaluated_at=datetime.utcnow(),
    )

    assert result.fit_evaluation_id == "fit-1"
    assert result.fit_status == FitEvaluationStatus.SUCCESS
    assert result.matching_strengths == []
    assert result.capability_gaps == []


def test_fit_evaluation_status_enum_values() -> None:
    assert FitEvaluationStatus.SUCCESS == "success"
    assert FitEvaluationStatus.WARNING == "warning"
    assert FitEvaluationStatus.FAILURE == "failure"
    assert FitEvaluationStatus("warning") is FitEvaluationStatus.WARNING


def test_fit_evaluation_result_list_defaults_are_isolated_per_instance() -> None:
    first = FitEvaluationResult(
        fit_evaluation_id="fit-1",
        analysis_id="analysis-1",
        profile_id="profile-1",
        fit_status=FitEvaluationStatus.SUCCESS,
        fit_score=0.8,
        confidence=0.85,
        evaluation_summary="First evaluation.",
        evaluated_at=datetime.utcnow(),
    )
    second = FitEvaluationResult(
        fit_evaluation_id="fit-2",
        analysis_id="analysis-2",
        profile_id="profile-2",
        fit_status=FitEvaluationStatus.SUCCESS,
        fit_score=0.7,
        confidence=0.75,
        evaluation_summary="Second evaluation.",
        evaluated_at=datetime.utcnow(),
    )

    first.matching_strengths.append("fastapi")
    first.capability_gaps.append("kubernetes")

    assert second.matching_strengths == []
    assert second.capability_gaps == []


def test_fit_evaluation_result_represents_strengths_gaps_and_positioning() -> None:
    result = FitEvaluationResult(
        fit_evaluation_id="fit-1",
        analysis_id="analysis-1",
        profile_id="profile-1",
        fit_status=FitEvaluationStatus.WARNING,
        fit_score=0.68,
        confidence=0.72,
        matching_strengths=["pipeline_design", "schema_modeling"],
        capability_gaps=["event_sourcing_depth"],
        high_risk_gaps=["distributed_tracing_at_scale"],
        low_risk_gaps=["grafana_dashboards"],
        positioning_advantages=["control_plane_experience"],
        positioning_concerns=["limited_enterprise_crm_exposure"],
        interview_readiness_signals=["can_explain_idempotent_ingest"],
        recommended_focus_areas=["integration_complexity_patterns"],
        evaluation_summary="Good fit with targeted interview preparation.",
        evaluated_at=datetime.utcnow(),
    )

    assert result.fit_status == FitEvaluationStatus.WARNING
    assert "pipeline_design" in result.matching_strengths
    assert "event_sourcing_depth" in result.capability_gaps
    assert "control_plane_experience" in result.positioning_advantages
    assert "limited_enterprise_crm_exposure" in result.positioning_concerns
