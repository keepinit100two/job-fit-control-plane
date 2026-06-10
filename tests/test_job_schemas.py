from datetime import datetime

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    AnalyzerLLMResult,
    ApplicationDecision,
    DecisionResult,
    DecisionStatus,
    JobPipelineResult,
    JobPosting,
    NormalizationResult,
    NormalizationStatus,
    NormalizedJobPostingEnvelope,
    RawJobPosting,
    FitEvaluationResult,
    FitEvaluationStatus,
    ProposalLLMResult,
    ProposalResult,
    ProposalStatus,
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
    assert pipeline_result.decision_result is None
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
    assert pipeline_result.decision_result is None


def _fit_evaluation_fixture() -> FitEvaluationResult:
    return FitEvaluationResult(
        fit_evaluation_id="fit-1",
        analysis_id="analysis-1",
        profile_id="profile-1",
        fit_status=FitEvaluationStatus.SUCCESS,
        fit_score=0.82,
        confidence=0.88,
        evaluation_summary="Strong alignment with role requirements.",
        evaluated_at=datetime.utcnow(),
    )


def test_job_pipeline_result_with_normalized_analysis_and_fit_evaluation() -> None:
    envelope = _normalized_envelope()
    analysis = _analysis_fixture()
    fit_evaluation = _fit_evaluation_fixture()
    pipeline_result = JobPipelineResult(
        normalized=envelope,
        analysis_result=analysis,
        fit_evaluation_result=fit_evaluation,
    )

    assert pipeline_result.analysis_result is analysis
    assert pipeline_result.fit_evaluation_result is fit_evaluation
    assert pipeline_result.fit_evaluation_result.fit_evaluation_id == "fit-1"
    assert pipeline_result.decision_result is None


def test_job_pipeline_result_with_full_pipeline_outputs() -> None:
    envelope = _normalized_envelope()
    analysis = _analysis_fixture()
    fit_evaluation = _fit_evaluation_fixture()
    decision = DecisionResult(
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.APPLY,
        decision_confidence=0.88,
        primary_reason="Strong fit score with no high-risk capability gaps.",
        decided_at=datetime.utcnow(),
    )
    pipeline_result = JobPipelineResult(
        normalized=envelope,
        analysis_result=analysis,
        fit_evaluation_result=fit_evaluation,
        decision_result=decision,
    )

    assert pipeline_result.analysis_result is analysis
    assert pipeline_result.fit_evaluation_result is fit_evaluation
    assert pipeline_result.decision_result is decision
    assert pipeline_result.decision_result.decision == ApplicationDecision.APPLY


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


def test_decision_result_instantiates_successfully() -> None:
    result = DecisionResult(
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.APPLY,
        decision_confidence=0.88,
        primary_reason="Strong fit score with manageable gaps.",
        decided_at=datetime.utcnow(),
    )

    assert result.decision_id == "decision-1"
    assert result.decision == ApplicationDecision.APPLY
    assert result.supporting_reasons == []
    assert result.blocking_concerns == []


def test_application_decision_enum_values() -> None:
    assert ApplicationDecision.APPLY == "apply"
    assert ApplicationDecision.MAYBE == "maybe"
    assert ApplicationDecision.SKIP == "skip"
    assert ApplicationDecision("maybe") is ApplicationDecision.MAYBE


def test_decision_status_enum_values() -> None:
    assert DecisionStatus.SUCCESS == "success"
    assert DecisionStatus.WARNING == "warning"
    assert DecisionStatus.FAILURE == "failure"
    assert DecisionStatus("warning") is DecisionStatus.WARNING


def test_decision_result_list_defaults_are_isolated_per_instance() -> None:
    first = DecisionResult(
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.APPLY,
        decision_confidence=0.9,
        primary_reason="First decision.",
        decided_at=datetime.utcnow(),
    )
    second = DecisionResult(
        decision_id="decision-2",
        analysis_id="analysis-2",
        fit_evaluation_id="fit-2",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.SKIP,
        decision_confidence=0.7,
        primary_reason="Second decision.",
        decided_at=datetime.utcnow(),
    )

    first.supporting_reasons.append("strong_python_match")
    first.blocking_concerns.append("oauth2_gap")

    assert second.supporting_reasons == []
    assert second.blocking_concerns == []


def test_decision_result_represents_apply_maybe_skip_context() -> None:
    apply_result = DecisionResult(
        decision_id="decision-apply",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.APPLY,
        decision_confidence=0.91,
        primary_reason="High fit score with strong alignment.",
        supporting_reasons=["pipeline_design_match"],
        recommended_next_steps=["prepare_portfolio_examples"],
        decided_at=datetime.utcnow(),
    )
    maybe_result = DecisionResult(
        decision_id="decision-maybe",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.WARNING,
        decision=ApplicationDecision.MAYBE,
        decision_confidence=0.62,
        primary_reason="Moderate fit with notable gaps.",
        follow_up_questions=["What is the team's OAuth experience?"],
        recommended_next_steps=["research_integration_patterns"],
        decided_at=datetime.utcnow(),
    )
    skip_result = DecisionResult(
        decision_id="decision-skip",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        decision_status=DecisionStatus.SUCCESS,
        decision=ApplicationDecision.SKIP,
        decision_confidence=0.85,
        primary_reason="High-risk gaps outweigh strengths.",
        blocking_concerns=["kubernetes_at_scale", "hipaa_compliance"],
        decided_at=datetime.utcnow(),
    )

    assert apply_result.decision == ApplicationDecision.APPLY
    assert maybe_result.decision == ApplicationDecision.MAYBE
    assert skip_result.decision == ApplicationDecision.SKIP
    assert apply_result.decision_status == DecisionStatus.SUCCESS
    assert maybe_result.decision_status == DecisionStatus.WARNING
    assert "kubernetes_at_scale" in skip_result.blocking_concerns


def test_proposal_result_instantiates_successfully() -> None:
    result = ProposalResult(
        proposal_id="proposal-1",
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        profile_id="profile-1",
        proposal_status=ProposalStatus.SUCCESS,
        proposal_confidence=0.87,
        positioning_strategy="Lead with control-plane and pipeline design experience.",
        proposal_summary="Tailored proposal for a strong-fit backend role.",
        generated_at=datetime.utcnow(),
    )

    assert result.proposal_id == "proposal-1"
    assert result.proposal_status == ProposalStatus.SUCCESS
    assert result.lead_strengths == []
    assert result.cover_letter_angles == []


def test_proposal_status_enum_values() -> None:
    assert ProposalStatus.SUCCESS == "success"
    assert ProposalStatus.WARNING == "warning"
    assert ProposalStatus.FAILURE == "failure"
    assert ProposalStatus("warning") is ProposalStatus.WARNING


def test_proposal_result_list_defaults_are_isolated_per_instance() -> None:
    first = ProposalResult(
        proposal_id="proposal-1",
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        profile_id="profile-1",
        proposal_status=ProposalStatus.SUCCESS,
        proposal_confidence=0.9,
        positioning_strategy="First proposal strategy.",
        proposal_summary="First proposal.",
        generated_at=datetime.utcnow(),
    )
    second = ProposalResult(
        proposal_id="proposal-2",
        decision_id="decision-2",
        analysis_id="analysis-2",
        fit_evaluation_id="fit-2",
        profile_id="profile-2",
        proposal_status=ProposalStatus.SUCCESS,
        proposal_confidence=0.8,
        positioning_strategy="Second proposal strategy.",
        proposal_summary="Second proposal.",
        generated_at=datetime.utcnow(),
    )

    first.lead_strengths.append("pipeline_design")
    first.interview_talking_points.append("idempotent_ingest")

    assert second.lead_strengths == []
    assert second.interview_talking_points == []


def test_proposal_result_represents_positioning_cover_letter_and_interview_context() -> None:
    result = ProposalResult(
        proposal_id="proposal-1",
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        profile_id="profile-1",
        proposal_status=ProposalStatus.SUCCESS,
        proposal_confidence=0.91,
        positioning_strategy="Position as a control-plane engineer with workflow automation depth.",
        lead_strengths=["pipeline_design", "schema_modeling"],
        strengths_to_emphasize=["fastapi", "event_driven_architecture"],
        gaps_to_address=["oauth2_integration"],
        project_examples=["job-fit-control-plane"],
        differentiators=["deterministic_pipeline_orchestration"],
        cover_letter_angles=[
            "Highlight end-to-end ingest-to-decision pipeline ownership.",
            "Emphasize schema-first subsystem design.",
        ],
        interview_talking_points=[
            "Explain idempotent ingest and normalization failure handling.",
            "Discuss hybrid deterministic + LLM enrichment approach.",
        ],
        questions_to_ask_employer=[
            "How mature is the existing workflow automation stack?",
        ],
        proposal_summary="Apply-focused proposal with interview preparation angles.",
        generated_at=datetime.utcnow(),
    )

    assert "control-plane engineer" in result.positioning_strategy
    assert "ingest-to-decision pipeline" in result.cover_letter_angles[0]
    assert "idempotent ingest" in result.interview_talking_points[0]
    assert "workflow automation" in result.questions_to_ask_employer[0]


def test_proposal_llm_result_instantiates_successfully() -> None:
    result = ProposalLLMResult(
        positioning_strategy="Lead with automation and integration depth.",
        proposal_summary="LLM-enriched proposal positioning.",
        llm_confidence=0.89,
    )

    assert result.positioning_strategy == "Lead with automation and integration depth."
    assert result.llm_confidence == 0.89
    assert result.strengths_to_emphasize == []
    assert result.warnings == []


def test_proposal_llm_result_list_defaults_are_isolated_per_instance() -> None:
    first = ProposalLLMResult(
        positioning_strategy="First strategy.",
        proposal_summary="First LLM proposal.",
        llm_confidence=0.9,
    )
    second = ProposalLLMResult(
        positioning_strategy="Second strategy.",
        proposal_summary="Second LLM proposal.",
        llm_confidence=0.8,
    )

    first.cover_letter_angles.append("angle-a")
    first.warnings.append("warning-a")

    assert second.cover_letter_angles == []
    assert second.warnings == []


def test_proposal_llm_confidence_is_separate_from_proposal_confidence() -> None:
    llm_result = ProposalLLMResult(
        positioning_strategy="LLM positioning output.",
        proposal_summary="LLM proposal output.",
        llm_confidence=0.93,
    )
    proposal_result = ProposalResult(
        proposal_id="proposal-1",
        decision_id="decision-1",
        analysis_id="analysis-1",
        fit_evaluation_id="fit-1",
        profile_id="profile-1",
        proposal_status=ProposalStatus.SUCCESS,
        proposal_confidence=0.61,
        positioning_strategy="Merged proposal positioning.",
        proposal_summary="Merged proposal output.",
        generated_at=datetime.utcnow(),
    )

    assert llm_result.llm_confidence == 0.93
    assert proposal_result.proposal_confidence == 0.61
    assert not hasattr(llm_result, "proposal_confidence")
    assert not hasattr(proposal_result, "llm_confidence")


def test_proposal_llm_result_represents_positioning_without_system_owned_ids() -> None:
    result = ProposalLLMResult(
        positioning_strategy="Position as a deterministic-pipeline specialist.",
        strengths_to_emphasize=["schema_first_design"],
        gaps_to_address=["enterprise_crm_depth"],
        differentiators=["hybrid_llm_enrichment"],
        cover_letter_angles=["Emphasize control-plane ownership."],
        interview_talking_points=["Walk through decision engine policy."],
        questions_to_ask_employer=["What does success look like in 90 days?"],
        proposal_summary="Strategic positioning from LLM enrichment.",
        llm_confidence=0.86,
        warnings=["Limited posting detail on team structure."],
    )

    assert "deterministic-pipeline" in result.positioning_strategy
    assert "schema_first_design" in result.strengths_to_emphasize
    assert "hybrid_llm_enrichment" in result.differentiators
    assert not hasattr(result, "proposal_id")
    assert not hasattr(result, "decision_id")
    assert not hasattr(result, "analysis_id")
    assert not hasattr(result, "fit_evaluation_id")
    assert not hasattr(result, "profile_id")
    assert not hasattr(result, "generated_at")
