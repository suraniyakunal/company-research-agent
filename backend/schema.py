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
