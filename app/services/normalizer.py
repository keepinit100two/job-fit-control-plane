from datetime import datetime
from typing import List
from uuid import uuid4

from app.domain.job_schemas import (
    JobPosting,
    NormalizationResult,
    NormalizationStatus,
    NormalizedJobPostingEnvelope,
    RawJobPosting,
)


def _raw_text_quality_score(length: int) -> float:
    if length > 500:
        return 0.9
    if length > 200:
        return 0.7
    return 0.5


def _first_line(text: str) -> str:
    line = text.splitlines()[0] if text.splitlines() else ""
    return line.strip()


def normalize_job_posting(raw: RawJobPosting) -> NormalizedJobPostingEnvelope:
    trimmed = raw.raw_text.strip()
    now = datetime.utcnow()
    quality_len = len(trimmed)

    if not trimmed or quality_len < 20:
        result = NormalizationResult(
            raw_posting_id=raw.raw_posting_id,
            content_hash=raw.content_hash,
            status=NormalizationStatus.FAILURE,
            confidence=0.0,
            raw_text_quality_score=_raw_text_quality_score(quality_len),
            used_llm=False,
            normalized_at=now,
        )
        return NormalizedJobPostingEnvelope(job_posting=None, normalization_result=result)

    used_raw_title = bool(raw.raw_title and raw.raw_title.strip())
    title = raw.raw_title.strip() if used_raw_title else _first_line(trimmed)
    if not title:
        title = "(untitled)"

    missing_required_fields: List[str] = []
    if not used_raw_title:
        missing_required_fields.append("title")

    job = JobPosting(
        job_posting_id=str(uuid4()),
        raw_posting_id=raw.raw_posting_id,
        content_hash=raw.content_hash,
        source=raw.source,
        source_url=raw.source_url,
        title=title,
        company_name=raw.raw_company_name,
        location=raw.raw_location,
        summary=trimmed,
        normalized_at=now,
    )

    result = NormalizationResult(
        raw_posting_id=raw.raw_posting_id,
        content_hash=raw.content_hash,
        status=NormalizationStatus.SUCCESS,
        confidence=0.6,
        raw_text_quality_score=_raw_text_quality_score(quality_len),
        missing_required_fields=missing_required_fields,
        used_llm=False,
        normalized_at=now,
    )

    return NormalizedJobPostingEnvelope(job_posting=job, normalization_result=result)
