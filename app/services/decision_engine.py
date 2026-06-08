from datetime import datetime
from uuid import uuid4

from app.domain.job_schemas import (
    AnalysisResult,
    ApplicationDecision,
    DecisionResult,
    DecisionStatus,
    FitEvaluationResult,
)


def _union_lists(*lists: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for items in lists:
        for item in items:
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged


class DecisionEngine:
    def decide(
        self,
        analysis: AnalysisResult,
        fit_evaluation: FitEvaluationResult,
    ) -> DecisionResult:
        decision = self._determine_decision(fit_evaluation)
        decision_status = (
            DecisionStatus.WARNING
            if decision == ApplicationDecision.MAYBE
            else DecisionStatus.SUCCESS
        )

        return DecisionResult(
            decision_id=str(uuid4()),
            analysis_id=analysis.analysis_id,
            fit_evaluation_id=fit_evaluation.fit_evaluation_id,
            decision_status=decision_status,
            decision=decision,
            decision_confidence=fit_evaluation.confidence,
            primary_reason=self._primary_reason(decision, fit_evaluation),
            supporting_reasons=_union_lists(
                fit_evaluation.matching_strengths,
                fit_evaluation.positioning_advantages,
            ),
            blocking_concerns=_union_lists(
                fit_evaluation.high_risk_gaps,
                fit_evaluation.positioning_concerns,
            ),
            follow_up_questions=self._follow_up_questions(decision, fit_evaluation),
            recommended_next_steps=self._recommended_next_steps(decision),
            decided_at=datetime.utcnow(),
        )

    def _determine_decision(
        self,
        fit_evaluation: FitEvaluationResult,
    ) -> ApplicationDecision:
        if (
            fit_evaluation.fit_score >= 0.75
            and not fit_evaluation.high_risk_gaps
        ):
            return ApplicationDecision.APPLY

        if (
            fit_evaluation.fit_score < 0.40
            or len(fit_evaluation.high_risk_gaps) >= 2
        ):
            return ApplicationDecision.SKIP

        return ApplicationDecision.MAYBE

    def _primary_reason(
        self,
        decision: ApplicationDecision,
        fit_evaluation: FitEvaluationResult,
    ) -> str:
        if decision == ApplicationDecision.APPLY:
            return "Strong fit score with no high-risk capability gaps."

        if decision == ApplicationDecision.SKIP:
            if fit_evaluation.fit_score < 0.40:
                return "Fit score below minimum threshold."
            return "Multiple high-risk capability gaps identified."

        return "Moderate fit score requires further evaluation."

    def _follow_up_questions(
        self,
        decision: ApplicationDecision,
        fit_evaluation: FitEvaluationResult,
    ) -> list[str]:
        if decision != ApplicationDecision.MAYBE:
            return []

        questions = [
            f"How would you address the gap in {gap}?"
            for gap in fit_evaluation.high_risk_gaps
        ]
        if not questions:
            questions = [
                f"Can you strengthen experience in {gap}?"
                for gap in fit_evaluation.capability_gaps[:3]
            ]
        if not questions:
            questions = [
                "What additional role details would change this decision?"
            ]
        return questions

    def _recommended_next_steps(
        self,
        decision: ApplicationDecision,
    ) -> list[str]:
        if decision == ApplicationDecision.APPLY:
            return [
                "Prepare tailored application materials.",
                "Review interview readiness signals.",
                "Draft proposal talking points.",
            ]

        if decision == ApplicationDecision.MAYBE:
            return [
                "Research unresolved capability gaps.",
                "Gather follow-up information before applying.",
            ]

        return [
            "Deprioritize this opportunity.",
            "Focus on roles with stronger alignment.",
        ]
