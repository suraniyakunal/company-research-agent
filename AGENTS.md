# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

- **Backend:** Python 3.13 (`backend/`), managed with `uv`; FastAPI + LangGraph + Pydantic v2
- **Frontend:** TypeScript, Next.js **16** + React **19** (`frontend/`), managed with `npm`

## Commands

### Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev    # development server
npm run build  # production build
npm run lint   # ESLint 9 flat-config
```

> **No test suite exists.** There are no test files or test config in this project.

## Non-Obvious Patterns

- **Next.js 16 / React 19 warning:** APIs and conventions differ from older training data. Check `node_modules/next/dist/docs/` before writing any Next.js-specific code. See `frontend/AGENTS.md`.
- **BYOK pattern:** API keys are accepted per-request (`ResearchRequest.gemini_api_key`, `ResearchRequest.serper_api_key`) and fall back to env vars. Always maintain this fallback: `api_key = state["gemini_api_key"] or os.getenv("GEMINI_API_KEY")`.
- **Structured LLM output:** The backend uses `llm.with_structured_output(CompanyReport)` — the Pydantic model is the contract. Changes to `backend/schema.py` must mirror `frontend/types.ts`.
- **"Say Unknown" instruction:** Agent prompts explicitly instruct the LLM to output `"Unknown"` rather than hallucinate. Preserve this in any prompt edits.
- **Frontend styling:** All CSS lives inside JSX `<style jsx>` blocks in `pages/index.tsx` using CSS variables (`--paper`, `--card`, `--accent`, etc.). There is no external CSS-in-JS library.
- **ESLint 9 flat config:** `frontend/eslint.config.mjs` uses the `defineConfig` API — not `.eslintrc`.
- **LangGraph agent:** Three nodes, strict linear edges: `plan_searches → run_searches → synthesize_report`. Each node function returns a partial `AgentState` dict, not a full state.

## Code Style

| Layer | Convention |
|---|---|
| Python filenames | `snake_case.py` |
| Python functions | `snake_case`, verb-first (e.g. `plan_searches`) |
| Python classes / Pydantic models | `PascalCase` |
| TypeScript filenames | `lowercase` or `_prefixed` for Next.js specials |
| TypeScript variables & functions | `camelCase` |
| TypeScript interfaces | `PascalCase` (`CompanyReport`, `OpenRole`) |
| CSS classes | `kebab-case` |

- TypeScript: strict mode enabled; use `@/*` absolute imports (alias for `frontend/`).
- Python: `Optional[str]` with default `None` for nullable fields; all Pydantic fields use `Field(description=...)`.

## Environment Variables

```
# backend/.env (not committed)
GEMINI_API_KEY=...
SERPER_API_KEY=...

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```
