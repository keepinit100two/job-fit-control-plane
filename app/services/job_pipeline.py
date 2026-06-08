from typing import Optional

from app.domain.job_schemas import (
    JobPipelineResult,
    NormalizationStatus,
    RawJobPosting,
    UserCapabilityProfile,
)
from app.services.analyzer import HybridAnalyzer
from app.services.decision_engine import DecisionEngine
from app.services.fit_evaluator import FitEvaluator
from app.services.normalizer import normalize_job_posting


def process_raw_job_posting(
    raw: RawJobPosting,
    analyzer: Optional[HybridAnalyzer] = None,
    profile: Optional[UserCapabilityProfile] = None,
    fit_evaluator: Optional[FitEvaluator] = None,
    decision_engine: Optional[DecisionEngine] = None,
) -> JobPipelineResult:
    normalized_envelope = normalize_job_posting(raw)

    if normalized_envelope.normalization_result.status == NormalizationStatus.FAILURE:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=None,
            fit_evaluation_result=None,
            decision_result=None,
        )

    if analyzer is None:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=None,
            fit_evaluation_result=None,
            decision_result=None,
        )

    analysis_result = None
    if normalized_envelope.job_posting is not None:
        analysis_result = analyzer.analyze(normalized_envelope.job_posting)

    if profile is None or fit_evaluator is None:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=analysis_result,
            fit_evaluation_result=None,
            decision_result=None,
        )

    fit_evaluation_result = None
    if analysis_result is not None:
        fit_evaluation_result = fit_evaluator.evaluate_fit(profile, analysis_result)

    if decision_engine is None:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=analysis_result,
            fit_evaluation_result=fit_evaluation_result,
            decision_result=None,
        )

    decision_result = None
    if fit_evaluation_result is not None and analysis_result is not None:
        decision_result = decision_engine.decide(analysis_result, fit_evaluation_result)

    return JobPipelineResult(
        normalized=normalized_envelope,
        analysis_result=analysis_result,
        fit_evaluation_result=fit_evaluation_result,
        decision_result=decision_result,
    )
