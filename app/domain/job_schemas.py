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
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILURE = "FAILURE"


class NormalizationIssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


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
