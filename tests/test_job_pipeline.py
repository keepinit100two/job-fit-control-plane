from datetime import datetime

from app.domain.job_schemas import (
    AnalysisResult,
    DecisionResult,
    FitEvaluationResult,
    JobPipelineResult,
    JobPosting,
    NormalizationStatus,
    RawJobPosting,
    UserCapabilityProfile,
)
from app.services.analyzer import HybridAnalyzer
from app.services.decision_engine import DecisionEngine
from app.services.fit_evaluator import FitEvaluator
from app.services.job_pipeline import process_raw_job_posting


def _raw(*, raw_text: str) -> RawJobPosting:
    return RawJobPosting(
        raw_posting_id="raw-1",
        source="test",
        capture_method="fixture",
        raw_text=raw_text,
        captured_at=datetime.utcnow(),
        content_hash="hash-1",
    )


def _profile() -> UserCapabilityProfile:
    return UserCapabilityProfile(
        profile_id="profile-1",
        primary_role_focus="backend_engineer",
        updated_at=datetime.utcnow(),
    )


def test_process_raw_job_posting_returns_success_for_valid_input() -> None:
    result = process_raw_job_posting(_raw(raw_text="x" * 25))

    assert isinstance(result, JobPipelineResult)
    assert result.normalized.normalization_result.status == NormalizationStatus.SUCCESS


def test_process_raw_job_posting_returns_failure_for_short_raw_text() -> None:
    result = process_raw_job_posting(_raw(raw_text="short"))

    assert result.normalized.normalization_result.status == NormalizationStatus.FAILURE


def test_failure_result_has_no_job_posting() -> None:
    result = process_raw_job_posting(_raw(raw_text="short"))

    assert result.normalized.job_posting is None


def test_success_result_has_job_posting() -> None:
    result = process_raw_job_posting(_raw(raw_text="x" * 25))

    assert result.normalized.job_posting is not None


def test_normalization_failure_returns_all_optional_outputs_none() -> None:
    result = process_raw_job_posting(_raw(raw_text="short"))

    assert isinstance(result, JobPipelineResult)
    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert result.normalized.normalization_result.status == NormalizationStatus.FAILURE


def test_analyzer_missing_returns_all_downstream_outputs_none() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        profile=_profile(),
        fit_evaluator=FitEvaluator(),
        decision_engine=DecisionEngine(),
    )

    assert result.normalized.job_posting is not None
    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None


def test_analyzer_only_returns_analysis_result() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert (
        result.analysis_result.job_posting_id
        == result.normalized.job_posting.job_posting_id
    )


def test_analyzer_and_fit_evaluator_returns_fit_without_decision() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
        profile=_profile(),
        fit_evaluator=FitEvaluator(),
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert isinstance(result.fit_evaluation_result, FitEvaluationResult)
    assert result.decision_result is None
    assert (
        result.fit_evaluation_result.analysis_id
        == result.analysis_result.analysis_id
    )


def test_full_pipeline_returns_decision_result() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
        profile=_profile(),
        fit_evaluator=FitEvaluator(),
        decision_engine=DecisionEngine(),
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert isinstance(result.fit_evaluation_result, FitEvaluationResult)
    assert isinstance(result.decision_result, DecisionResult)
    assert (
        result.decision_result.analysis_id
        == result.analysis_result.analysis_id
    )
    assert (
        result.decision_result.fit_evaluation_id
        == result.fit_evaluation_result.fit_evaluation_id
    )


def test_valid_raw_posting_with_analyzer_but_no_profile_returns_no_fit() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
        fit_evaluator=FitEvaluator(),
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert result.fit_evaluation_result is None
    assert result.decision_result is None


class TrackingAnalyzer:
    def __init__(self) -> None:
        self.called = False

    def analyze(self, job_posting: JobPosting) -> AnalysisResult:
        self.called = True
        return HybridAnalyzer().analyze(job_posting)


class TrackingFitEvaluator:
    def __init__(self) -> None:
        self.called = False

    def evaluate_fit(
        self,
        profile: UserCapabilityProfile,
        analysis: AnalysisResult,
    ) -> FitEvaluationResult:
        self.called = True
        return FitEvaluator().evaluate_fit(profile, analysis)


class TrackingDecisionEngine:
    def __init__(self) -> None:
        self.called = False

    def decide(
        self,
        analysis: AnalysisResult,
        fit_evaluation: FitEvaluationResult,
    ) -> DecisionResult:
        self.called = True
        return DecisionEngine().decide(analysis, fit_evaluation)


def test_analyzer_not_called_when_normalization_fails() -> None:
    tracking = TrackingAnalyzer()
    result = process_raw_job_posting(
        _raw(raw_text="short"),
        analyzer=tracking,
    )

    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert tracking.called is False


def test_fit_evaluator_not_called_when_normalization_fails() -> None:
    tracking = TrackingFitEvaluator()
    result = process_raw_job_posting(
        _raw(raw_text="short"),
        analyzer=HybridAnalyzer(),
        profile=_profile(),
        fit_evaluator=tracking,
    )

    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert tracking.called is False


def test_fit_evaluator_not_called_when_analyzer_missing() -> None:
    tracking = TrackingFitEvaluator()
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        profile=_profile(),
        fit_evaluator=tracking,
    )

    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert tracking.called is False


def test_decision_engine_not_called_when_fit_evaluation_missing() -> None:
    tracking = TrackingDecisionEngine()
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
        decision_engine=tracking,
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert tracking.called is False


def test_decision_engine_not_called_when_analyzer_missing() -> None:
    tracking = TrackingDecisionEngine()
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        profile=_profile(),
        fit_evaluator=FitEvaluator(),
        decision_engine=tracking,
    )

    assert result.analysis_result is None
    assert result.fit_evaluation_result is None
    assert result.decision_result is None
    assert tracking.called is False
