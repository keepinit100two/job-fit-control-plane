from datetime import datetime

import pytest

from app.domain.job_schemas import AnalyzerLLMResult, JobPosting
from app.services.llm_adapter import LLMAdapterResult
from app.services.openai_adapter import OpenAIAnalyzerAdapter


def _job_posting() -> JobPosting:
    return JobPosting(
        job_posting_id="job-1",
        raw_posting_id="raw-1",
        content_hash="hash-1",
        source="test",
        title="Senior Python Engineer",
        summary="Build backend services and automation pipelines.",
        normalized_at=datetime.utcnow(),
    )


def _llm_result() -> AnalyzerLLMResult:
    return AnalyzerLLMResult(
        system_type="control_plane",
        tier_classification="tier_2",
        reasoning_summary="Backend automation role.",
        llm_confidence=0.82,
    )


def test_missing_api_key_returns_success_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    adapter = OpenAIAnalyzerAdapter(api_key=None)

    result = adapter.analyze_job_posting(_job_posting())

    assert result.success is False
    assert result.error_message == "OPENAI_API_KEY is missing"
    assert result.llm_result is None
    assert result.model_name == "gpt-4.1-mini"


def test_successful_fake_structured_response_returns_llm_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _llm_result()

    def fake_call_openai(self: OpenAIAnalyzerAdapter, job_posting: JobPosting) -> AnalyzerLLMResult:
        assert job_posting.title == "Senior Python Engineer"
        return expected

    monkeypatch.setattr(OpenAIAnalyzerAdapter, "_call_openai", fake_call_openai)
    adapter = OpenAIAnalyzerAdapter(api_key="test-key")

    result = adapter.analyze_job_posting(_job_posting())

    assert result.success is True
    assert result.llm_result == expected
    assert result.model_name == "gpt-4.1-mini"
    assert result.error_message is None


def test_exception_from_openai_returns_success_false(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_call_openai(self: OpenAIAnalyzerAdapter, job_posting: JobPosting) -> AnalyzerLLMResult:
        raise RuntimeError("network down")

    monkeypatch.setattr(OpenAIAnalyzerAdapter, "_call_openai", fake_call_openai)
    adapter = OpenAIAnalyzerAdapter(api_key="test-key", max_retries=1)

    result = adapter.analyze_job_posting(_job_posting())

    assert result.success is False
    assert result.llm_result is None
    assert result.error_message == "network down"
    assert result.model_name == "gpt-4.1-mini"


def test_adapter_does_not_raise_raw_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_call_openai(self: OpenAIAnalyzerAdapter, job_posting: JobPosting) -> AnalyzerLLMResult:
        raise ValueError("boom")

    monkeypatch.setattr(OpenAIAnalyzerAdapter, "_call_openai", fake_call_openai)
    adapter = OpenAIAnalyzerAdapter(api_key="test-key", max_retries=0)

    result = adapter.analyze_job_posting(_job_posting())

    assert isinstance(result, LLMAdapterResult)
    assert result.success is False
    assert result.error_message == "boom"
