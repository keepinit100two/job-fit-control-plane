from typing import Optional, Protocol

from pydantic import BaseModel

from app.domain.job_schemas import AnalyzerLLMResult, JobPosting


class LLMAdapterResult(BaseModel):
    success: bool
    llm_result: Optional[AnalyzerLLMResult] = None
    error_message: Optional[str] = None
    raw_response: Optional[str] = None
    model_name: Optional[str] = None


class AnalyzerLLMAdapter(Protocol):
    def analyze_job_posting(self, job_posting: JobPosting) -> LLMAdapterResult: ...
