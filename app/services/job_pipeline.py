from app.domain.job_schemas import (
    NormalizationStatus,
    NormalizedJobPostingEnvelope,
    RawJobPosting,
)
from app.services.normalizer import normalize_job_posting


def process_raw_job_posting(raw: RawJobPosting) -> NormalizedJobPostingEnvelope:
    envelope = normalize_job_posting(raw)
    if envelope.normalization_result.status == NormalizationStatus.FAILURE:
        return envelope
    return envelope
