from datetime import datetime
from uuid import uuid4

from app.domain.job_schemas import (
    AnalysisResult,
    FitEvaluationResult,
    FitEvaluationStatus,
    UserCapabilityProfile,
)

_HIGH_RISK_KEYWORDS = (
    "oauth",
    "oauth2",
    "kubernetes",
    "k8s",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "production infrastructure",
    "security",
    "compliance",
    "hipaa",
)

_ARCHITECTURE_AI_SIGNAL_KEYWORDS = ("architect", "ai", "llm", "gpt")


def _normalize_item(item: str) -> str:
    return item.strip().lower()


def _normalize_set(items: list[str]) -> set[str]:
    return {_normalize_item(item) for item in items if item and item.strip()}


def _dedupe_requirements(items: list[str]) -> list[str]:
    seen: set[str] = set()
    requirements: list[str] = []
    for item in items:
        if not item or not item.strip():
            continue
        normalized = _normalize_item(item)
        if normalized in seen:
            continue
        seen.add(normalized)
        requirements.append(item.strip())
    return requirements


def _is_high_risk_gap(gap: str) -> bool:
    lowered = gap.lower()
    return any(keyword in lowered for keyword in _HIGH_RISK_KEYWORDS)


def _is_architecture_or_ai_strength(strength: str) -> bool:
    lowered = strength.lower()
    return any(keyword in lowered for keyword in _ARCHITECTURE_AI_SIGNAL_KEYWORDS)


class FitEvaluator:
    def evaluate_fit(
        self,
        profile: UserCapabilityProfile,
        analysis: AnalysisResult,
    ) -> FitEvaluationResult:
        user_capabilities = _build_user_capabilities(profile)
        job_requirements = _build_job_requirements(analysis)

        matching_strengths = [
            requirement
            for requirement in job_requirements
            if _normalize_item(requirement) in user_capabilities
        ]
        capability_gaps = [
            requirement
            for requirement in job_requirements
            if _normalize_item(requirement) not in user_capabilities
        ]
        high_risk_gaps = [gap for gap in capability_gaps if _is_high_risk_gap(gap)]
        low_risk_gaps = [gap for gap in capability_gaps if gap not in high_risk_gaps]

        if not job_requirements:
            fit_score = 0.5
            confidence = 0.4
            fit_status = FitEvaluationStatus.WARNING
        else:
            fit_score = min(
                1.0,
                max(0.0, len(matching_strengths) / len(job_requirements)),
            )
            confidence = 0.7
            fit_status = FitEvaluationStatus.SUCCESS

        positioning_advantages = [
            f"Strong alignment with {strength}" for strength in matching_strengths
        ]
        positioning_concerns = [
            f"High-risk gap: {gap}" for gap in high_risk_gaps
        ]
        interview_readiness_signals = [
            strength
            for strength in matching_strengths
            if _is_architecture_or_ai_strength(strength)
        ]
        recommended_focus_areas = list(high_risk_gaps) + list(low_risk_gaps)

        evaluation_summary = (
            f"Fit evaluation complete: {len(matching_strengths)} matches, "
            f"{len(capability_gaps)} gaps, fit score {fit_score:.2f}."
        )

        return FitEvaluationResult(
            fit_evaluation_id=str(uuid4()),
            analysis_id=analysis.analysis_id,
            profile_id=profile.profile_id,
            fit_status=fit_status,
            fit_score=fit_score,
            confidence=confidence,
            matching_strengths=matching_strengths,
            capability_gaps=capability_gaps,
            high_risk_gaps=high_risk_gaps,
            low_risk_gaps=low_risk_gaps,
            positioning_advantages=positioning_advantages,
            positioning_concerns=positioning_concerns,
            interview_readiness_signals=interview_readiness_signals,
            recommended_focus_areas=recommended_focus_areas,
            evaluation_summary=evaluation_summary,
            evaluated_at=datetime.utcnow(),
        )


def _build_user_capabilities(profile: UserCapabilityProfile) -> set[str]:
    return _normalize_set(
        profile.programming_languages
        + profile.frameworks_and_libraries
        + profile.infrastructure_tools
        + profile.ai_capabilities
        + profile.automation_capabilities
        + profile.architecture_patterns
        + profile.deployment_capabilities
        + profile.integration_capabilities
        + profile.project_experience
        + profile.domain_experience
        + profile.strongest_capabilities
        + profile.communication_capabilities
        + profile.preferred_work_types
    )


def _build_job_requirements(analysis: AnalysisResult) -> list[str]:
    return _dedupe_requirements(
        analysis.core_capabilities_required
        + analysis.architecture_signals
        + analysis.business_problem_categories
        + analysis.hardest_interview_concepts
    )
