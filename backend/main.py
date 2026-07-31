# backend/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schema import ResearchRequest, CompanyReport
from agent import run_research

load_dotenv()

app = FastAPI(title="Company Research Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# In-memory set of IPs that have consumed their one free lookup.
# Resets on server restart — no persistence needed for this use case.
used_ips: set[str] = set()


@app.post("/research", response_model=CompanyReport)
def research(body: ResearchRequest, request: Request) -> CompanyReport:
    client_ip: str = request.client.host

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

    try:
        result = run_research(body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Only record the IP when server keys were consumed.
    if using_server_keys:
        used_ips.add(client_ip)

    return result
