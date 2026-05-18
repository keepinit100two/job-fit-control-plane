from datetime import datetime

from app.domain.job_schemas import NormalizationStatus, RawJobPosting
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
    envelope = process_raw_job_posting(_raw(raw_text="x" * 25))

    assert envelope.normalization_result.status == NormalizationStatus.SUCCESS


def test_process_raw_job_posting_returns_failure_for_short_raw_text() -> None:
    envelope = process_raw_job_posting(_raw(raw_text="short"))

    assert envelope.normalization_result.status == NormalizationStatus.FAILURE


def test_failure_result_has_no_job_posting() -> None:
    envelope = process_raw_job_posting(_raw(raw_text="short"))

    assert envelope.job_posting is None


def test_success_result_has_job_posting() -> None:
    envelope = process_raw_job_posting(_raw(raw_text="x" * 25))

    assert envelope.job_posting is not None
