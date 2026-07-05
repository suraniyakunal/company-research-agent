# backend/main.py

from fastapi import FastAPI, HTTPException
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


@app.post("/research", response_model=CompanyReport)
def research(request: ResearchRequest) -> CompanyReport:
    try:
        return run_research(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
