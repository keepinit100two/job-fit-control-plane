from datetime import datetime

import pytest

from app.domain.job_schemas import NormalizationStatus, RawJobPosting
from app.services.normalizer import normalize_job_posting


def _raw(
    *,
    raw_text: str,
    raw_title=None,
    raw_posting_id="raw-1",
    content_hash="hash-1",
) -> RawJobPosting:
    return RawJobPosting(
        raw_posting_id=raw_posting_id,
        source="test",
        capture_method="fixture",
        raw_text=raw_text,
        captured_at=datetime.utcnow(),
        content_hash=content_hash,
        raw_title=raw_title,
    )


def test_valid_raw_returns_success_and_job_posting() -> None:
    text = "x" * 25
    raw = _raw(raw_text=text)
    envelope = normalize_job_posting(raw)

    assert envelope.normalization_result.status == NormalizationStatus.SUCCESS
    assert envelope.job_posting is not None
    assert envelope.job_posting.summary == text
    assert envelope.job_posting.raw_posting_id == raw.raw_posting_id


def test_short_raw_text_returns_failure_and_no_job_posting() -> None:
    raw = _raw(raw_text="short")
    envelope = normalize_job_posting(raw)

    assert envelope.normalization_result.status == NormalizationStatus.FAILURE
    assert envelope.job_posting is None
    assert envelope.normalization_result.confidence == 0.0


def test_title_fallback_uses_first_line_when_raw_title_missing() -> None:
    raw = _raw(
        raw_text="First line title here\n\nMore body " + "x" * 30,
        raw_title=None,
    )
    envelope = normalize_job_posting(raw)

    assert envelope.job_posting is not None
    assert envelope.job_posting.title == "First line title here"
    assert "title" in envelope.normalization_result.missing_required_fields


@pytest.mark.parametrize(
    ("pad_len", "expected_score"),
    [
        (201, 0.7),
        (501, 0.9),
    ],
)
def test_raw_text_quality_score_thresholds(pad_len: int, expected_score: float) -> None:
    base = "a" * 20
    raw = _raw(raw_text=base + "x" * (pad_len - len(base)))
    envelope = normalize_job_posting(raw)

    assert envelope.normalization_result.raw_text_quality_score == expected_score


def test_raw_text_quality_score_else_branch() -> None:
    raw = _raw(raw_text="y" * 100)
    envelope = normalize_job_posting(raw)

    assert len(raw.raw_text) <= 200
    assert envelope.normalization_result.raw_text_quality_score == 0.5
