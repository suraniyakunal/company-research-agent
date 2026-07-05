# backend/agent.py

import os
import requests
from typing import TypedDict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from schema import CompanyReport, ResearchRequest


class AgentState(TypedDict):
    company_name: str
    user_profile: str
    gemini_api_key: Optional[str]
    serper_api_key: Optional[str]
    search_queries: List[str]
    search_results: str
    report: CompanyReport


def plan_searches(state: AgentState) -> dict:
    api_key = state["gemini_api_key"] or os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

    prompt = f"""You are researching the company "{state["company_name"]}" for a job applicant.
Generate exactly 4 short, specific Google search queries that would together reveal:
1. What the company does and its tech stack
2. Founders, CEO, and key leadership names, plus funding history and company size
3. Recent news or product launches
4. Current open engineering/AI job roles

Return ONLY the 4 queries, one per line, no numbering, no extra text."""

    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]

    return {"search_queries": queries}


def run_searches(state: AgentState) -> dict:
    api_key = state["serper_api_key"] or os.getenv("SERPER_API_KEY")
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    combined_results = ""
    for query in state["search_queries"]:
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json={"q": query},
            timeout=10,
        )
        data = response.json()

        combined_results += f"\n--- Results for: {query} ---\n"
        for item in data.get("organic", [])[:5]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            combined_results += f"{title}\n{snippet}\nSource: {link}\n\n"

    return {"search_results": combined_results}


def synthesize_report(state: AgentState) -> dict:
    api_key = state["gemini_api_key"] or os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
    structured_llm = llm.with_structured_output(CompanyReport)

    prompt = f"""Using ONLY the search results below, build a research report on "{state["company_name"]}".

If information for a field isn't in the search results, use the literal string "Unknown" for that entire field (not partial info combined with "Unknown") — do NOT invent facts.

For fit_score and fit_reasoning, evaluate this candidate's background against the company:
{state["user_profile"]}

SEARCH RESULTS:
{state["search_results"]}
"""

    report = structured_llm.invoke(prompt)
    return {"report": report}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("plan_searches", plan_searches)
    graph.add_node("run_searches", run_searches)
    graph.add_node("synthesize_report", synthesize_report)

    graph.add_edge(START, "plan_searches")
    graph.add_edge("plan_searches", "run_searches")
    graph.add_edge("run_searches", "synthesize_report")
    graph.add_edge("synthesize_report", END)

    return graph.compile()


_compiled_graph = build_graph()


def run_research(request: ResearchRequest) -> CompanyReport:
    initial_state: AgentState = {
        "company_name": request.company_name,
        "user_profile": request.user_profile,
        "gemini_api_key": request.gemini_api_key,
        "serper_api_key": request.serper_api_key,
        "search_queries": [],
        "search_results": "",
        "report": None,
    }
    final_state = _compiled_graph.invoke(initial_state)
    return final_state["report"]
