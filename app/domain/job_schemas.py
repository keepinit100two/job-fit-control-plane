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
