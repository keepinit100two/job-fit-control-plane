from datetime import datetime

from app.domain.job_schemas import AnalyzerLLMResult, JobPosting
from app.services.llm_adapter import AnalyzerLLMAdapter, LLMAdapterResult


def _job_posting() -> JobPosting:
    return JobPosting(
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        source="test",
        title="Senior Python Engineer",
        summary="Build and maintain backend services.",
        normalized_at=datetime.utcnow(),
    )


def test_llm_adapter_result_success_with_analyzer_llm_result() -> None:
    llm_result = AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Enriched by adapter.",
        llm_confidence=0.88,
    )
    adapter_result = LLMAdapterResult(
        success=True,
        llm_result=llm_result,
        model_name="fake-model",
    )

    assert adapter_result.success is True
    assert adapter_result.llm_result is not None
    assert adapter_result.llm_result.llm_confidence == 0.88
    assert adapter_result.error_message is None


def test_llm_adapter_result_failure_without_llm_result() -> None:
    adapter_result = LLMAdapterResult(
        success=False,
        error_message="Adapter unavailable",
    )

    assert adapter_result.success is False
    assert adapter_result.llm_result is None
    assert adapter_result.error_message == "Adapter unavailable"


class FakeAnalyzerLLMAdapter:
    def analyze_job_posting(self, job_posting: JobPosting) -> LLMAdapterResult:
        return LLMAdapterResult(
            success=True,
            llm_result=AnalyzerLLMResult(
                system_type="control_plane",
                tier_classification="tier_2",
                reasoning_summary=f"Analyzed {job_posting.title}",
                llm_confidence=0.75,
            ),
            model_name="fake-model",
        )


def test_fake_adapter_implements_protocol_and_returns_result() -> None:
    adapter: AnalyzerLLMAdapter = FakeAnalyzerLLMAdapter()
    result = adapter.analyze_job_posting(_job_posting())

    assert result.success is True
    assert result.llm_result is not None
    assert "Senior Python Engineer" in result.llm_result.reasoning_summary
