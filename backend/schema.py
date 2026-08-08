from pydantic import BaseModel, Field
from typing import List, Optional


class OpenRole(BaseModel):
    """A single open job posting at the company."""

    title: str = Field(
        description="Exact job title as posted, e.g. 'Backend Engineer' or 'Founding AI Engineer'"
    )
    link: str = Field(description="Direct URL to the job posting page")


class ResearchRequest(BaseModel):
    """What the API endpoint receives from the frontend."""

    company_name: str = Field(description="Name of the company to research")
    user_profile: str = Field(
        description="Free-text summary of the requesting user's skills, experience, and background, "
        "used to compute fit_score and fit_reasoning against this company"
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="User's own Gemini API key. If omitted, server falls back to its own key.",
    )
    serper_api_key: Optional[str] = Field(
        default=None,
        description="User's own Serper API key. If omitted, server falls back to its own key.",
    )


class CompanyReport(BaseModel):
    """Structured research report on a single company, generated for Kunal's job-hunt use case."""

    company_name: str = Field(
        description="Official name of the company as it appears on their website"
    )
    one_liner: str = Field(
        description="A single sentence describing what the company builds and for whom"
    )
    tech_stack: List[str] = Field(
        description="Programming languages, frameworks, and infra tools this company is known to use, "
        "based on job postings, engineering blog posts, or GitHub"
    )
    team_size: str = Field(
        description="Approximate company size as a range, e.g. '11-50 employees', "
        "or 'Unknown' if no reliable source found"
    )
    key_people: List[str] = Field(
        description="Names and titles of founders and key leadership, e.g. 'Jane Doe - CEO & Co-founder'"
    )
    funding: str = Field(
        description="Latest known funding stage and amount, e.g. 'Seed - $3.2M (2024)', "
        "or 'Unknown' if not publicly disclosed"
    )
    recent_news: List[str] = Field(
        description="Notable recent announcements, launches, or press mentions from the last 6-12 months"
    )
    open_roles: List[OpenRole] = Field(
        description="Currently open engineering or AI-related roles at this company, if any are listed"
    )
    pain_points: List[str] = Field(
        description="Inferred technical or product challenges this company likely faces right now, "
        "based on their stage, stack, and recent news — the kind of problems an AI engineer "
        "hire would be brought in to solve"
    )
    fit_score: int = Field(
        ge=1,
        le=10,
        description="Score from 1 (poor fit) to 10 (excellent fit) rating how well the requesting "
        "user's background matches this company's likely needs",
    )
    fit_reasoning: str = Field(
        description="2-3 sentences explaining the fit_score, referencing specific overlaps or gaps "
        "between the user's skills and this company's tech stack, stage, and open roles"
    )
    sources: List[str] = Field(
        description="URLs actually used to compile this report — every field's information should be "
        "traceable to one of these"
    )


# ---------------------------------------------------------------------------
# Analytics / stats
# ---------------------------------------------------------------------------


class TopCompany(BaseModel):
    """A single entry in the most-researched companies list."""

    name: str = Field(description="Company name")
    count: int = Field(description="Number of successful research runs")


class DailyActivity(BaseModel):
    """Search count for a single calendar day (used in the /analytics dashboard)."""

    date: str = Field(description="ISO date string, e.g. '2025-08-01'")
    count: int = Field(description="Number of research requests that day")


class StatsResponse(BaseModel):
    """Aggregate analytics returned by GET /stats."""

    total_searches: int = Field(description="All-time research request count")
    unique_sessions: int = Field(description="Distinct anonymous session IDs seen")
    success_rate: float = Field(description="Fraction of requests that completed successfully (0–1)")
    searches_last_7_days: int = Field(description="Requests in the past 7 days")
    searches_last_30_days: int = Field(description="Requests in the past 30 days")
    top_companies: List[TopCompany] = Field(description="Up to 10 most-researched companies")

    # Detailed fields — only present when ?detailed=true
    searches_prev_7_days: Optional[int] = Field(
        default=None, description="Requests in the 7 days before the current 7-day window"
    )
    daily_activity: Optional[List[DailyActivity]] = Field(
        default=None, description="Per-day breakdown for the past 30 days"
    )
    byok_count: Optional[int] = Field(
        default=None, description="Requests that supplied their own API keys"
    )
    free_count: Optional[int] = Field(
        default=None, description="Requests that used the shared server keys"
    )
    avg_duration_ms: Optional[int] = Field(
        default=None, description="Average successful research duration in milliseconds"
    )
