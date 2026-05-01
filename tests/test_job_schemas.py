from datetime import datetime

from app.domain.job_schemas import (
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
