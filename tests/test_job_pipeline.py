from datetime import datetime

from app.domain.job_schemas import (
    AnalysisResult,
    JobPipelineResult,
    JobPosting,
    NormalizationStatus,
    RawJobPosting,
)
from app.services.analyzer import HybridAnalyzer
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


def test_normalization_failure_returns_pipeline_result_without_analysis() -> None:
    result = process_raw_job_posting(_raw(raw_text="short"))

    assert isinstance(result, JobPipelineResult)
    assert result.analysis_result is None
    assert result.normalized.normalization_result.status == NormalizationStatus.FAILURE


def test_valid_raw_posting_without_analyzer_returns_no_analysis() -> None:
    result = process_raw_job_posting(_raw(raw_text="x" * 25))

    assert result.normalized.job_posting is not None
    assert result.analysis_result is None


def test_valid_raw_posting_with_analyzer_returns_analysis_result() -> None:
    result = process_raw_job_posting(
        _raw(raw_text="x" * 25),
        analyzer=HybridAnalyzer(),
    )

    assert isinstance(result.analysis_result, AnalysisResult)
    assert result.normalized.job_posting is not None
    assert (
        result.analysis_result.job_posting_id
        == result.normalized.job_posting.job_posting_id
    )


class TrackingAnalyzer:
    def __init__(self) -> None:
        self.called = False

    def analyze(self, job_posting: JobPosting) -> AnalysisResult:
        self.called = True
        return HybridAnalyzer().analyze(job_posting)


def test_analyzer_not_called_when_normalization_fails() -> None:
    tracking = TrackingAnalyzer()
    result = process_raw_job_posting(
        _raw(raw_text="short"),
        analyzer=tracking,
    )

    assert result.analysis_result is None
    assert tracking.called is False
