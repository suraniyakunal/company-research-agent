# Company Research Agent

Given a company name, this agent plans its own searches, gathers public information from the web, and returns a structured research report — including a fit score against a candidate's background — in under a minute.

Built to speed up cold-outreach research before applying to YC-backed startups, but works for any company and any candidate profile.

**Live demo:** [link once deployed]
**API docs:** [link once deployed]/docs

---

## What it actually does

1. You give it a company name and a short profile of your background.
2. A LangGraph agent plans 4 targeted search queries (tech stack, leadership/funding, recent news, open roles).
3. Those queries run against live web search (Serper).
4. A second LLM call reads the raw results and synthesizes a structured report — validated against a strict schema, so the output shape is guaranteed, not just "probably JSON."
5. The same call scores 1–10 how well the given profile fits this company, with reasoning tied to specific overlaps (skills, stack, open roles).

This isn't a search wrapper — the planning and synthesis are two separate, purposeful LLM calls, and the agent is explicitly instructed to say "Unknown" rather than invent facts it didn't find.

---

## Architecture

```
Next.js (frontend)
      │  POST /research
      ▼
FastAPI (backend)
      │
      ▼
LangGraph agent
  ┌─────────────────┐
  │ plan_searches    │  → Gemini decides 4 search queries
  ├─────────────────┤
  │ run_searches     │  → Serper API executes them
  ├─────────────────┤
  │ synthesize_report│  → Gemini + structured output → CompanyReport
  └─────────────────┘
```

**Backend:** Python, FastAPI, LangGraph, `langchain-google-genai`, Pydantic
**LLM:** Google Gemini 2.5 Flash
**Search:** Serper API
**Frontend:** Next.js (TypeScript), no UI framework — hand-styled
**Deploy:** Render (backend) + Vercel (frontend)

---

## Why these choices

- **LangGraph over a single prompt-and-parse call** — the agent plans its own search queries instead of me hardcoding them. That's the difference between a scraper and an agent: it reasons about *what* to look for before looking.
- **Pydantic + `with_structured_output`** — the final response is schema-validated, not just "the LLM was told to return JSON." If Gemini ever returns a malformed field (e.g. a `fit_score` outside 1–10), it fails loudly instead of shipping broken data to the frontend.
- **BYOK (bring your own key)** — anyone can use this tool with their own Gemini/Serper keys, or fall back to the shared demo keys. This exists specifically so the tool isn't just useful to me — it's a real multi-user tool, not a personal script, and it protects the demo from one user burning the shared quota.
- **Explicit "say Unknown, don't invent" instruction** — the single most important line in the synthesis prompt. Structured output enforces *shape*; this instruction is what limits hallucination.

---

## Output schema

```python
class CompanyReport(BaseModel):
    company_name: str
    one_liner: str
    tech_stack: List[str]
    team_size: str
    key_people: List[str]
    funding: str
    recent_news: List[str]
    open_roles: List[OpenRole]       # {title, link}
    pain_points: List[str]           # inferred, not scraped
    fit_score: int                   # 1-10, validated
    fit_reasoning: str
    sources: List[str]               # every field should trace back to one of these
```

---

## Running locally

### Backend

```bash
cd backend
uv sync
```

Create `backend/.env`:
```
GEMINI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
```

```bash
uv run uvicorn main:app --reload --port 8000
```

Test it directly:
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Ramp", "user_profile": "Python, FastAPI, React, built a RAG pipeline"}'
```

Interactive API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
npm run dev
```

Open `http://localhost:3000`.

---

## Known limitations

- **Search-dependent accuracy.** If a company has little public presence, several fields correctly return "Unknown" rather than guessing — this is intentional, not a bug, but it does mean smaller/stealth companies produce thinner reports.
- **No rate limiting on the demo endpoint.** Fine for a portfolio project; would need per-IP limiting before any real production use.
- **No caching.** Researching the same company twice re-runs the full pipeline (2 LLM calls + 4 searches) instead of reusing a recent result.
- **Serper's top-5-per-query results only.** Occasionally misses a field (e.g. funding) that's publicly available but didn't surface in the top results for that specific query.

---

## About

Built by **Kunal Suraniya** — MERN stack developer transitioning into AI Engineering.

- GitHub: [github.com/suraniyakunal](https://github.com/suraniyakunal)
- LinkedIn: [linkedin.com/in/kunalsuraniya](https://linkedin.com/in/kunalsuraniya)
