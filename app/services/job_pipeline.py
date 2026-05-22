from typing import Optional

from app.domain.job_schemas import (
    JobPipelineResult,
    NormalizationStatus,
    RawJobPosting,
)
from app.services.analyzer import HybridAnalyzer
from app.services.normalizer import normalize_job_posting


def process_raw_job_posting(
    raw: RawJobPosting,
    analyzer: Optional[HybridAnalyzer] = None,
) -> JobPipelineResult:
    normalized_envelope = normalize_job_posting(raw)

    if normalized_envelope.normalization_result.status == NormalizationStatus.FAILURE:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=None,
        )

    if analyzer is None or normalized_envelope.job_posting is None:
        return JobPipelineResult(
            normalized=normalized_envelope,
            analysis_result=None,
        )

    analysis_result = analyzer.analyze(normalized_envelope.job_posting)
    return JobPipelineResult(
        normalized=normalized_envelope,
        analysis_result=analysis_result,
    )
