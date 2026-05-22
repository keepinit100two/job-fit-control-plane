from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.domain.job_schemas import (
    AnalysisResult,
    AnalysisStatus,
    AnalyzerLLMResult,
    JobPosting,
)
from app.services.llm_adapter import AnalyzerLLMAdapter


def _searchable_text(job_posting: JobPosting) -> str:
    return f"{job_posting.title} {job_posting.summary}".lower()


def _union_lists(*lists: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for items in lists:
        for item in items:
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged


class HybridAnalyzer:
    def __init__(
        self,
        llm_adapter: Optional[AnalyzerLLMAdapter] = None,
        use_llm: bool = False,
    ) -> None:
        self._llm_adapter = llm_adapter
        self._use_llm = use_llm

    def analyze(self, job_posting: JobPosting) -> AnalysisResult:
        analysis_id = str(uuid4())
        analyzed_at = datetime.utcnow()
        baseline = self._build_baseline(job_posting, analysis_id, analyzed_at)

        if not self._use_llm or self._llm_adapter is None:
            return baseline

        adapter_result = self._llm_adapter.analyze_job_posting(job_posting)

        if adapter_result.success and adapter_result.llm_result is not None:
            return self._merge_llm_result(baseline, adapter_result.llm_result)

        baseline.analysis_status = AnalysisStatus.WARNING
        baseline.analysis_confidence = 0.4
        if adapter_result.error_message:
            baseline.analysis_issues.append(adapter_result.error_message)
        return baseline

    def _build_baseline(
        self,
        job_posting: JobPosting,
        analysis_id: str,
        analyzed_at: datetime,
    ) -> AnalysisResult:
        text = _searchable_text(job_posting)

        system_type = "unknown"
        tier_classification = "unknown"
        pipeline_pattern: Optional[str] = None
        ai_involvement_level: Optional[str] = None
        architecture_signals: list[str] = []
        business_problem_categories: list[str] = []

        if any(
            keyword in text
            for keyword in ("automation", "workflow", "zapier", "make")
        ):
            system_type = "workflow_automation"

        if any(keyword in text for keyword in ("ai", "openai", "gpt", "llm")):
            ai_involvement_level = "bounded_ai_step"

        if any(keyword in text for keyword in ("api", "webhook", "integration")):
            architecture_signals.append("api_integration")

        if any(keyword in text for keyword in ("crm", "hubspot", "salesforce")):
            business_problem_categories.append("crm_workflow")

        if any(
            keyword in text
            for keyword in ("dashboard", "reporting", "analytics")
        ):
            business_problem_categories.append("reporting_automation")

        return AnalysisResult(
            analysis_id=analysis_id,
            job_posting_id=job_posting.job_posting_id,
            raw_posting_id=job_posting.raw_posting_id,
            content_hash=job_posting.content_hash,
            analysis_status=AnalysisStatus.SUCCESS,
            analysis_confidence=0.5,
            system_type=system_type,
            tier_classification=tier_classification,
            pipeline_pattern=pipeline_pattern,
            ai_involvement_level=ai_involvement_level,
            architecture_signals=architecture_signals,
            business_problem_categories=business_problem_categories,
            reasoning_summary="Deterministic baseline analysis completed.",
            analyzed_at=analyzed_at,
        )

    def _merge_llm_result(
        self,
        baseline: AnalysisResult,
        llm_result: AnalyzerLLMResult,
    ) -> AnalysisResult:
        return AnalysisResult(
            analysis_id=baseline.analysis_id,
            job_posting_id=baseline.job_posting_id,
            raw_posting_id=baseline.raw_posting_id,
            content_hash=baseline.content_hash,
            analyzed_at=baseline.analyzed_at,
            analysis_status=baseline.analysis_status,
            analysis_issues=list(baseline.analysis_issues),
            system_type=llm_result.system_type,
            tier_classification=llm_result.tier_classification,
            pipeline_pattern=llm_result.pipeline_pattern,
            ai_involvement_level=llm_result.ai_involvement_level,
            automation_level=llm_result.automation_level,
            integration_complexity=llm_result.integration_complexity,
            core_capabilities_required=_union_lists(
                baseline.core_capabilities_required,
                llm_result.core_capabilities_required,
            ),
            architecture_signals=_union_lists(
                baseline.architecture_signals,
                llm_result.architecture_signals,
            ),
            business_problem_categories=_union_lists(
                baseline.business_problem_categories,
                llm_result.business_problem_categories,
            ),
            hardest_interview_concepts=_union_lists(
                baseline.hardest_interview_concepts,
                llm_result.hardest_interview_concepts,
            ),
            missing_information=_union_lists(
                baseline.missing_information,
                llm_result.missing_information,
            ),
            reasoning_summary=llm_result.reasoning_summary,
            analysis_confidence=llm_result.llm_confidence,
        )
