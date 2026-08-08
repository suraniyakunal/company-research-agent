# backend/main.py

import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schema import ResearchRequest, CompanyReport, StatsResponse
from agent import run_research
from database import init_db, log_event, get_stats

load_dotenv()

app = FastAPI(title="Company Research Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialise the analytics database (no-ops gracefully if DATABASE_URL is absent).
init_db()

# In-memory set of IPs that have consumed their one free lookup.
# Resets on server restart — no persistence needed for this use case.
used_ips: set[str] = set()


@app.post("/research", response_model=CompanyReport)
def research(body: ResearchRequest, request: Request) -> CompanyReport:
    client_ip: str = request.client.host
    session_id: Optional[str] = request.headers.get("X-Session-ID")

    # A request is "using server keys" when the caller has not supplied both keys.
    using_server_keys: bool = not (body.gemini_api_key and body.serper_api_key)

    if using_server_keys and client_ip in used_ips:
        raise HTTPException(
            status_code=429,
            detail=(
                "You have used your free lookup. "
                "Please provide your own Gemini and Serper API keys."
            ),
        )

    start_time = time.monotonic()
    try:
        result = run_research(body)
    except Exception as e:
        duration_ms = int((time.monotonic() - start_time) * 1000)
        log_event(
            session_id=session_id,
            company_name=body.company_name,
            fit_score=None,
            is_byok=not using_server_keys,
            success=False,
            duration_ms=duration_ms,
        )
        raise HTTPException(status_code=500, detail=str(e))

    duration_ms = int((time.monotonic() - start_time) * 1000)
    log_event(
        session_id=session_id,
        company_name=body.company_name,
        fit_score=result.fit_score,
        is_byok=not using_server_keys,
        success=True,
        duration_ms=duration_ms,
    )

    # Only record the IP when server keys were consumed.
    if using_server_keys:
        used_ips.add(client_ip)

    return result


@app.get("/stats", response_model=StatsResponse)
def stats(detailed: bool = False) -> StatsResponse:
    """
    Public aggregate analytics endpoint.
    Pass ?detailed=true for the full breakdown (used by the /analytics dashboard).
    """
    return get_stats(detailed=detailed)
