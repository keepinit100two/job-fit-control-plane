import os
from typing import List, Optional

from app.domain.job_schemas import AnalyzerLLMResult, JobPosting
from app.services.llm_adapter import LLMAdapterResult

_SYSTEM_PROMPT = """You analyze software, automation, AI, and backend job postings.

Return structured enrichment matching the AnalyzerLLMResult schema only.

Rules:
- Do not output apply, skip, maybe, or any application decision.
- Do not generate cover letters or proposals.
- Use "unknown" for uncertain categorical string fields.
- Keep reasoning_summary concise (one or two sentences).
- Populate list fields with relevant signals from the posting; use empty lists when none apply.
- Set llm_confidence between 0.0 and 1.0 reflecting how well the posting supports your analysis.
"""


class OpenAIAnalyzerAdapter:
    def __init__(
        self,
        model_name: str = "gpt-4.1-mini",
        max_retries: int = 1,
        api_key: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.max_retries = max_retries
        self._api_key = api_key

    def _resolve_api_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        return os.environ.get("OPENAI_API_KEY")

    def _build_prompt(self, job_posting: JobPosting) -> str:
        sections: List[str] = [
            f"Title: {job_posting.title}",
            f"Company: {job_posting.company_name or 'unknown'}",
            f"Source: {job_posting.source}",
            f"Location: {job_posting.location or 'unknown'}",
            f"Client type: {job_posting.client_type or 'unknown'}",
            f"Employment type: {job_posting.employment_type or 'unknown'}",
            f"Location type: {job_posting.location_type or 'unknown'}",
            "",
            "Summary:",
            job_posting.summary,
        ]

        list_fields = [
            ("Responsibilities", job_posting.responsibilities),
            ("Deliverables", job_posting.deliverables),
            ("Required skills", job_posting.required_skills),
            ("Preferred skills", job_posting.preferred_skills),
            ("Tools and platforms", job_posting.tools_and_platforms),
            ("Domain keywords", job_posting.domain_keywords),
            ("Business problem signals", job_posting.business_problem_signals),
            ("Seniority signals", job_posting.seniority_signals),
            ("Timeline signals", job_posting.timeline_signals),
            ("Constraints", job_posting.constraints),
            ("Red flags", job_posting.red_flags),
        ]
        for label, items in list_fields:
            if items:
                sections.append("")
                sections.append(f"{label}:")
                sections.extend(f"- {item}" for item in items)

        if job_posting.budget_or_compensation:
            sections.extend(["", f"Budget or compensation: {job_posting.budget_or_compensation}"])

        return "\n".join(sections)

    def _call_openai(self, job_posting: JobPosting) -> AnalyzerLLMResult:
        from openai import OpenAI

        client = OpenAI(api_key=self._resolve_api_key())
        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": self._build_prompt(job_posting)},
            ],
            response_format=AnalyzerLLMResult,
        )
        message = completion.choices[0].message
        if message.refusal:
            raise ValueError("Model refused the request")
        if message.parsed is None:
            raise ValueError("Structured parse returned no result")
        return message.parsed

    def analyze_job_posting(self, job_posting: JobPosting) -> LLMAdapterResult:
        api_key = self._resolve_api_key()
        if not api_key:
            return LLMAdapterResult(
                success=False,
                error_message="OPENAI_API_KEY is missing",
                model_name=self.model_name,
            )

        attempts = self.max_retries + 1
        last_error = "OpenAI analysis failed"

        for _ in range(attempts):
            try:
                llm_result = self._call_openai(job_posting)
                return LLMAdapterResult(
                    success=True,
                    llm_result=llm_result,
                    model_name=self.model_name,
                )
            except Exception as exc:
                last_error = self._safe_error_message(exc)

        return LLMAdapterResult(
            success=False,
            error_message=last_error,
            model_name=self.model_name,
        )

    @staticmethod
    def _safe_error_message(exc: Exception) -> str:
        message = str(exc).strip()
        if not message:
            return type(exc).__name__
        if len(message) > 200:
            return message[:200]
        return message
