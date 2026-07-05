// frontend/pages/index.tsx

import { useState } from "react";
import Head from "next/head";
import type { CompanyReport } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEFAULT_PROFILE =
  "MCA graduate, MERN stack developer transitioning into AI Engineering. " +
  "Skills: Python, FastAPI, Node.js, React, MongoDB, Docker. " +
  "Built a RAG pipeline from scratch (LangChain + Chroma + Gemini). " +
  "Built a real-time voice platform using Mediasoup SFU supporting 100+ concurrent users. " +
  "No professional experience yet, targeting AI Engineering roles.";

export default function Home() {
  const [companyName, setCompanyName] = useState("");
  const [userProfile, setUserProfile] = useState(DEFAULT_PROFILE);
  const [geminiKey, setGeminiKey] = useState("");
  const [serperKey, setSerperKey] = useState("");
  const [showKeys, setShowKeys] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<CompanyReport | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const res = await fetch(`${API_URL}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: companyName,
          user_profile: userProfile,
          gemini_api_key: geminiKey || null,
          serper_api_key: serperKey || null,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Something went wrong while researching this company.");
      }

      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Head>
        <title>Company Research Agent</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </Head>

      <main className="page">
        <header className="eyebrow-block">
          <span className="eyebrow">CASE FILE // 001</span>
          <h1>Company Research Agent</h1>
          <p className="sub">
            Enter a company name. The agent plans searches, gathers public data, and scores the fit
            against a candidate profile — in under a minute.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="intake">
          <label className="field">
            <span>Company name</span>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Ramp, Vercel, Retool"
              required
            />
          </label>

          <label className="field">
            <span>Candidate profile</span>
            <textarea
              value={userProfile}
              onChange={(e) => setUserProfile(e.target.value)}
              rows={4}
              required
            />
          </label>

          <button
            type="button"
            className="disclosure"
            onClick={() => setShowKeys(!showKeys)}
          >
            {showKeys ? "− Hide" : "+ Use"} your own API keys (optional)
          </button>

          {showKeys && (
            <div className="key-row">
              <label className="field">
                <span>Gemini API key</span>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="Leave blank to use the shared key"
                  autoComplete="off"
                />
              </label>
              <label className="field">
                <span>Serper API key</span>
                <input
                  type="password"
                  value={serperKey}
                  onChange={(e) => setSerperKey(e.target.value)}
                  placeholder="Leave blank to use the shared key"
                  autoComplete="off"
                />
              </label>
            </div>
          )}

          <button type="submit" className="submit" disabled={loading}>
            {loading ? "Researching…" : "Run research"}
          </button>
          {loading && <p className="loading-note">Planning searches, reading results, writing the report. ~15–30s.</p>}
        </form>

        {error && (
          <div className="error-box">
            <strong>Research failed.</strong> {error}
          </div>
        )}

        {report && (
          <section className="dossier">
            <div className="stamp">{report.fit_score}/10</div>

            <h2>{report.company_name}</h2>
            <p className="one-liner">{report.one_liner}</p>

            <div className="grid">
              <div>
                <h3>Tech stack</h3>
                <div className="tags">
                  {report.tech_stack.map((t) => (
                    <span key={t} className="tag">{t}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3>Team size</h3>
                <p className="mono">{report.team_size}</p>
              </div>
              <div>
                <h3>Funding</h3>
                <p className="mono">{report.funding}</p>
              </div>
              <div>
                <h3>Key people</h3>
                <ul>{report.key_people.map((p) => <li key={p}>{p}</li>)}</ul>
              </div>
            </div>

            <div className="block">
              <h3>Recent news</h3>
              <ul>{report.recent_news.map((n) => <li key={n}>{n}</li>)}</ul>
            </div>

            <div className="block">
              <h3>Open roles</h3>
              <ul>
                {report.open_roles.map((role) => (
                  <li key={role.link}>
                    <a href={role.link} target="_blank" rel="noopener noreferrer">{role.title}</a>
                  </li>
                ))}
              </ul>
            </div>

            <div className="block">
              <h3>Likely pain points</h3>
              <ul>{report.pain_points.map((p) => <li key={p}>{p}</li>)}</ul>
            </div>

            <div className="block fit">
              <h3>Fit reasoning</h3>
              <p>{report.fit_reasoning}</p>
            </div>

            <div className="block sources">
              <h3>Sources</h3>
              <ul className="mono">
                {report.sources.map((s) => (
                  <li key={s}><a href={s} target="_blank" rel="noopener noreferrer">{s}</a></li>
                ))}
              </ul>
            </div>
          </section>
        )}
      </main>

      <style jsx global>{`
        :root {
          --paper: #ece7dd;
          --card: #f7f4ee;
          --ink: #1c2127;
          --ink-soft: #565b66;
          --accent: #b8863b;
          --line: #cdc6b3;
          --danger: #7a3327;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          background: var(--paper);
          color: var(--ink);
          font-family: "Inter", sans-serif;
        }
        a { color: var(--accent); }
      `}</style>

      <style jsx>{`
        .page {
          max-width: 760px;
          margin: 0 auto;
          padding: 48px 20px 96px;
        }
        .eyebrow-block { margin-bottom: 32px; }
        .eyebrow {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          letter-spacing: 0.12em;
          color: var(--ink-soft);
        }
        h1 {
          font-family: "Fraunces", serif;
          font-size: 34px;
          font-weight: 600;
          margin: 8px 0 12px;
        }
        .sub { color: var(--ink-soft); max-width: 520px; line-height: 1.5; }

        .intake {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .field { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
        .field span { color: var(--ink-soft); font-weight: 500; }
        input, textarea {
          font-family: "Inter", sans-serif;
          font-size: 15px;
          padding: 10px 12px;
          border: 1px solid var(--line);
          border-radius: 6px;
          background: white;
          color: var(--ink);
          resize: vertical;
        }
        .disclosure {
          align-self: flex-start;
          background: none;
          border: none;
          color: var(--accent);
          font-size: 13px;
          font-family: "IBM Plex Mono", monospace;
          cursor: pointer;
          padding: 0;
        }
        .key-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        .submit {
          align-self: flex-start;
          background: var(--ink);
          color: var(--paper);
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          font-size: 15px;
          cursor: pointer;
        }
        .submit:disabled { opacity: 0.6; cursor: default; }
        .loading-note { font-size: 13px; color: var(--ink-soft); margin: -4px 0 0; }

        .error-box {
          margin-top: 20px;
          background: #f4e6e1;
          border: 1px solid var(--danger);
          color: var(--danger);
          padding: 14px 16px;
          border-radius: 8px;
          font-size: 14px;
        }

        .dossier {
          position: relative;
          margin-top: 32px;
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 32px;
        }
        .stamp {
          position: absolute;
          top: 24px;
          right: 28px;
          font-family: "IBM Plex Mono", monospace;
          font-weight: 500;
          border: 2px dashed var(--accent);
          color: var(--accent);
          border-radius: 50%;
          width: 64px;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(-8deg);
          font-size: 14px;
        }
        h2 {
          font-family: "Fraunces", serif;
          font-size: 26px;
          margin: 0 0 8px;
          max-width: 80%;
        }
        .one-liner { color: var(--ink-soft); line-height: 1.5; max-width: 85%; }
        h3 {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          letter-spacing: 0.08em;
          color: var(--ink-soft);
          margin: 0 0 8px;
          text-transform: uppercase;
        }
        .grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin: 24px 0;
        }
        .tags { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          background: var(--paper);
          border: 1px solid var(--line);
          padding: 3px 8px;
          border-radius: 100px;
        }
        .mono { font-family: "IBM Plex Mono", monospace; font-size: 14px; }
        .block { margin-top: 20px; border-top: 1px solid var(--line); padding-top: 16px; }
        ul { margin: 0; padding-left: 18px; line-height: 1.6; }
        .sources ul { font-size: 12px; word-break: break-all; }

        @media (max-width: 600px) {
          .grid, .key-row { grid-template-columns: 1fr; }
        }
      `}</style>
    </>
  );
}
