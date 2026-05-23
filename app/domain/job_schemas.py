from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RawJobPosting(BaseModel):
    raw_posting_id: str
    source: str
    source_url: Optional[str] = None
    capture_method: str
    raw_title: Optional[str] = None
    raw_company_name: Optional[str] = None
    raw_location: Optional[str] = None
    raw_text: str
    captured_at: datetime
    content_hash: str


class JobPosting(BaseModel):
    job_posting_id: str
    raw_posting_id: str
    content_hash: str
    source: str
    source_url: Optional[str] = None
    title: str
    company_name: Optional[str] = None
    client_type: Optional[str] = None
    employment_type: Optional[str] = None
    location_type: Optional[str] = None
    location: Optional[str] = None
    summary: str
    responsibilities: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    tools_and_platforms: List[str] = Field(default_factory=list)
    domain_keywords: List[str] = Field(default_factory=list)
    business_problem_signals: List[str] = Field(default_factory=list)
    seniority_signals: List[str] = Field(default_factory=list)
    budget_or_compensation: Optional[str] = None
    timeline_signals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    normalized_at: datetime


class NormalizationStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"


class NormalizationIssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class NormalizationIssue(BaseModel):
    field: Optional[str] = None
    severity: NormalizationIssueSeverity
    message: str


class NormalizationResult(BaseModel):
    raw_posting_id: str
    content_hash: str
    status: NormalizationStatus
    confidence: float
    raw_text_quality_score: float
    issues: List[NormalizationIssue] = Field(default_factory=list)
    missing_required_fields: List[str] = Field(default_factory=list)
    inferred_fields: List[str] = Field(default_factory=list)
    ambiguous_fields: List[str] = Field(default_factory=list)
    used_llm: bool
    model_name: Optional[str] = None
    normalized_at: datetime


class NormalizedJobPostingEnvelope(BaseModel):
    job_posting: Optional[JobPosting] = None
    normalization_result: NormalizationResult


class AnalysisStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"


class AnalysisResult(BaseModel):
    analysis_id: str
    job_posting_id: str
    raw_posting_id: str
    content_hash: str
    analysis_status: AnalysisStatus
    analysis_confidence: float
    analysis_issues: List[str] = Field(default_factory=list)
    system_type: str
    tier_classification: str
    pipeline_pattern: Optional[str] = None
    ai_involvement_level: Optional[str] = None
    automation_level: Optional[str] = None
    integration_complexity: Optional[str] = None
    core_capabilities_required: List[str] = Field(default_factory=list)
    architecture_signals: List[str] = Field(default_factory=list)
    business_problem_categories: List[str] = Field(default_factory=list)
    hardest_interview_concepts: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    reasoning_summary: str
    analyzed_at: datetime


class AnalyzerLLMResult(BaseModel):
    system_type: str
    tier_classification: str
    pipeline_pattern: Optional[str] = None
    ai_involvement_level: Optional[str] = None
    automation_level: Optional[str] = None
    integration_complexity: Optional[str] = None
    core_capabilities_required: List[str] = Field(default_factory=list)
    architecture_signals: List[str] = Field(default_factory=list)
    business_problem_categories: List[str] = Field(default_factory=list)
    hardest_interview_concepts: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    reasoning_summary: str
    llm_confidence: float
    warnings: List[str] = Field(default_factory=list)


class JobPipelineResult(BaseModel):
    normalized: NormalizedJobPostingEnvelope
    analysis_result: Optional[AnalysisResult] = None


class UserCapabilityProfile(BaseModel):
    profile_id: str
    primary_role_focus: str
    programming_languages: List[str] = Field(default_factory=list)
    frameworks_and_libraries: List[str] = Field(default_factory=list)
    infrastructure_tools: List[str] = Field(default_factory=list)
    ai_capabilities: List[str] = Field(default_factory=list)
    automation_capabilities: List[str] = Field(default_factory=list)
    architecture_patterns: List[str] = Field(default_factory=list)
    deployment_capabilities: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)
    project_experience: List[str] = Field(default_factory=list)
    domain_experience: List[str] = Field(default_factory=list)
    strongest_capabilities: List[str] = Field(default_factory=list)
    weaker_capabilities: List[str] = Field(default_factory=list)
    communication_capabilities: List[str] = Field(default_factory=list)
    preferred_work_types: List[str] = Field(default_factory=list)
    updated_at: datetime


class FitEvaluationStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    FAILURE = "failure"


class FitEvaluationResult(BaseModel):
    fit_evaluation_id: str
    analysis_id: str
    profile_id: str
    fit_status: FitEvaluationStatus
    fit_score: float
    confidence: float
    matching_strengths: List[str] = Field(default_factory=list)
    capability_gaps: List[str] = Field(default_factory=list)
    high_risk_gaps: List[str] = Field(default_factory=list)
    low_risk_gaps: List[str] = Field(default_factory=list)
    positioning_advantages: List[str] = Field(default_factory=list)
    positioning_concerns: List[str] = Field(default_factory=list)
    interview_readiness_signals: List[str] = Field(default_factory=list)
    recommended_focus_areas: List[str] = Field(default_factory=list)
    evaluation_summary: str
    evaluated_at: datetime
