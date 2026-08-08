// frontend/pages/analytics.tsx

import { useState, useEffect } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import type { StatsResponse } from "../types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const EXPECTED_KEY = process.env.NEXT_PUBLIC_ANALYTICS_KEY || "kunal@123";

export default function Analytics() {
  const router = useRouter();
  const [keyInput, setKeyInput] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState(false);

  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check query param or session storage on load
  useEffect(() => {
    if (!router.isReady) return;

    const queryKey = router.query.key as string | undefined;
    const storedKey = typeof window !== "undefined" ? sessionStorage.getItem("analytics_key") : null;
    const keyToTest = queryKey || storedKey;

    if (keyToTest === EXPECTED_KEY) {
      Promise.resolve().then(() => setIsAuthenticated(true));
      if (typeof window !== "undefined") {
        sessionStorage.setItem("analytics_key", keyToTest);
      }
    }
  }, [router.isReady, router.query.key]);

  // Fetch detailed stats once authenticated
  useEffect(() => {
    if (!isAuthenticated) return;

    Promise.resolve().then(() => setLoading(true));
    fetch(`${API_URL}/stats?detailed=true`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: StatsResponse) => setStats(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (keyInput === EXPECTED_KEY) {
      setIsAuthenticated(true);
      setAuthError(false);
      sessionStorage.setItem("analytics_key", keyInput);
    } else {
      setAuthError(true);
    }
  }

  if (!isAuthenticated) {
    return (
      <>
        <Head>
          <title>Analytics Login | Company Research Agent</title>
        </Head>
        <main className="gate-page">
          <div className="gate-card">
            <span className="eyebrow">YC DEMO // DASHBOARD</span>
            <h1>Analytics Portal</h1>
            <p className="sub">Enter your access key to view real-time user metrics.</p>

            <form onSubmit={handleLogin} className="gate-form">
              <input
                type="password"
                placeholder="Access key"
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                required
                autoFocus
              />
              <button type="submit">Access Dashboard</button>
            </form>
            {authError && <p className="error">Invalid access key.</p>}
          </div>

          <style jsx>{`
            .gate-page {
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #ece7dd;
              font-family: "Inter", sans-serif;
              padding: 20px;
            }
            .gate-card {
              background: #f7f4ee;
              border: 1px solid #cdc6b3;
              border-radius: 12px;
              padding: 36px;
              max-width: 400px;
              width: 100%;
              text-align: center;
            }
            .eyebrow {
              font-family: "IBM Plex Mono", monospace;
              font-size: 11px;
              letter-spacing: 0.1em;
              color: #565b66;
            }
            h1 {
              font-family: "Fraunces", serif;
              font-size: 26px;
              margin: 10px 0 6px;
              color: #1c2127;
            }
            .sub {
              font-size: 14px;
              color: #565b66;
              margin-bottom: 24px;
            }
            .gate-form {
              display: flex;
              flex-direction: column;
              gap: 12px;
            }
            input {
              padding: 12px;
              border: 1px solid #cdc6b3;
              border-radius: 6px;
              font-size: 14px;
              background: #ffffff;
            }
            button {
              background: #1c2127;
              color: #ece7dd;
              border: none;
              padding: 12px;
              border-radius: 6px;
              font-weight: 500;
              cursor: pointer;
            }
            .error {
              color: #7a3327;
              font-size: 13px;
              margin-top: 12px;
            }
          `}</style>
        </main>
      </>
    );
  }

  const weeklyGrowth = stats?.searches_prev_7_days
    ? Math.round(((stats.searches_last_7_days - stats.searches_prev_7_days) / stats.searches_prev_7_days) * 100)
    : null;

  return (
    <>
      <Head>
        <title>Analytics Dashboard | Company Research Agent</title>
      </Head>

      <main className="dashboard">
        <header className="dash-header">
          <div>
            <span className="eyebrow">YC DEMO // TELEMETRY</span>
            <h1>Usage Analytics</h1>
          </div>
          <button
            onClick={() => {
              sessionStorage.removeItem("analytics_key");
              setIsAuthenticated(false);
            }}
            className="logout-btn"
          >
            Lock Dashboard
          </button>
        </header>

        {loading && <p className="status-msg">Loading real-time metrics...</p>}
        {error && <p className="error-msg">Failed to load analytics: {error}</p>}

        {stats && (
          <>
            {/* Top Metric Cards */}
            <section className="metrics-grid">
              <div className="card">
                <span className="label">Total Searches</span>
                <span className="value">{stats.total_searches.toLocaleString()}</span>
                <span className="subtext">{stats.searches_last_30_days} in last 30 days</span>
              </div>

              <div className="card">
                <span className="label">Unique Sessions</span>
                <span className="value">{stats.unique_sessions.toLocaleString()}</span>
                <span className="subtext">Cookieless browser fingerprints</span>
              </div>

              <div className="card">
                <span className="label">7-Day Activity</span>
                <span className="value">{stats.searches_last_7_days}</span>
                <span className="subtext">
                  {weeklyGrowth !== null
                    ? `${weeklyGrowth >= 0 ? "+" : ""}${weeklyGrowth}% vs prev 7 days`
                    : "Past week queries"}
                </span>
              </div>

              <div className="card">
                <span className="label">Success Rate</span>
                <span className="value">{Math.round(stats.success_rate * 100)}%</span>
                <span className="subtext">
                  Avg dur: {stats.avg_duration_ms ? `${(stats.avg_duration_ms / 1000).toFixed(1)}s` : "N/A"}
                </span>
              </div>
            </section>

            {/* Split Grid: Usage Breakdown & Top Companies */}
            <section className="details-grid">
              <div className="panel">
                <h3>Key Breakdown (BYOK vs Free)</h3>
                <div className="ratio-bar-container">
                  <div className="ratio-bar">
                    <div
                      className="ratio-fill byok"
                      style={{
                        width: `${
                          stats.total_searches
                            ? ((stats.byok_count || 0) / stats.total_searches) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                  <div className="ratio-legend">
                    <div>
                      <span className="dot byok-dot" /> BYOK Key: {stats.byok_count || 0}
                    </div>
                    <div>
                      <span className="dot free-dot" /> Server Key (Free): {stats.free_count || 0}
                    </div>
                  </div>
                </div>
              </div>

              <div className="panel">
                <h3>Top Researched Companies</h3>
                {stats.top_companies.length === 0 ? (
                  <p className="empty-state">No company searches logged yet.</p>
                ) : (
                  <ul className="company-list">
                    {stats.top_companies.map((c, i) => (
                      <li key={c.name}>
                        <span className="rank">#{i + 1}</span>
                        <span className="c-name">{c.name}</span>
                        <span className="c-count">{c.count} {c.count === 1 ? "search" : "searches"}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </section>

            {/* Daily Activity spark chart */}
            {stats.daily_activity && stats.daily_activity.length > 0 && (
              <section className="panel chart-panel">
                <h3>30-Day Activity Trend</h3>
                <div className="chart-bars">
                  {stats.daily_activity.map((d) => {
                    const maxCount = Math.max(...(stats.daily_activity?.map((x) => x.count) || [1]));
                    const heightPct = Math.max((d.count / maxCount) * 100, 8);
                    return (
                      <div key={d.date} className="bar-wrapper" title={`${d.date}: ${d.count} searches`}>
                        <div className="bar" style={{ height: `${heightPct}%` }} />
                        <span className="bar-label">{d.date.slice(5)}</span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}
          </>
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
        }
        body {
          background: var(--paper);
          color: var(--ink);
          font-family: "Inter", sans-serif;
          margin: 0;
        }
      `}</style>

      <style jsx>{`
        .dashboard {
          max-width: 900px;
          margin: 0 auto;
          padding: 40px 20px 80px;
        }
        .dash-header {
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          margin-bottom: 32px;
        }
        .eyebrow {
          font-family: "IBM Plex Mono", monospace;
          font-size: 11px;
          letter-spacing: 0.12em;
          color: var(--ink-soft);
        }
        h1 {
          font-family: "Fraunces", serif;
          font-size: 32px;
          margin: 4px 0 0;
        }
        .logout-btn {
          background: none;
          border: 1px solid var(--line);
          padding: 8px 14px;
          border-radius: 6px;
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          cursor: pointer;
          color: var(--ink-soft);
        }
        .logout-btn:hover {
          color: var(--ink);
          border-color: var(--ink);
        }
        .status-msg,
        .error-msg {
          font-family: "IBM Plex Mono", monospace;
          font-size: 14px;
          color: var(--ink-soft);
        }
        .error-msg {
          color: #7a3327;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        .card {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 20px;
          display: flex;
          flex-direction: column;
        }
        .label {
          font-family: "IBM Plex Mono", monospace;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--ink-soft);
        }
        .value {
          font-family: "Fraunces", serif;
          font-size: 32px;
          font-weight: 600;
          margin: 8px 0 4px;
          color: var(--ink);
        }
        .subtext {
          font-size: 12px;
          color: var(--accent);
          font-family: "IBM Plex Mono", monospace;
        }

        .details-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 24px;
        }
        .panel {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: 10px;
          padding: 24px;
        }
        h3 {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--ink-soft);
          margin: 0 0 16px;
        }

        .ratio-bar-container {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .ratio-bar {
          height: 12px;
          background: #d4cebe;
          border-radius: 6px;
          overflow: hidden;
        }
        .ratio-fill.byok {
          height: 100%;
          background: var(--accent);
        }
        .ratio-legend {
          display: flex;
          gap: 24px;
          font-size: 13px;
          font-family: "IBM Plex Mono", monospace;
        }
        .dot {
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-right: 6px;
        }
        .byok-dot {
          background: var(--accent);
        }
        .free-dot {
          background: #d4cebe;
        }

        .company-list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .company-list li {
          display: flex;
          align-items: center;
          font-size: 14px;
        }
        .rank {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          color: var(--ink-soft);
          width: 28px;
        }
        .c-name {
          font-weight: 500;
          flex: 1;
        }
        .c-count {
          font-family: "IBM Plex Mono", monospace;
          font-size: 12px;
          color: var(--accent);
        }
        .empty-state {
          font-size: 13px;
          color: var(--ink-soft);
          font-style: italic;
        }

        .chart-panel {
          margin-top: 24px;
        }
        .chart-bars {
          display: flex;
          align-items: flex-end;
          gap: 8px;
          height: 140px;
          padding-top: 16px;
        }
        .bar-wrapper {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100%;
          justify-content: flex-end;
        }
        .bar {
          width: 100%;
          max-width: 24px;
          background: var(--accent);
          border-radius: 3px 3px 0 0;
          min-height: 4px;
        }
        .bar-label {
          font-family: "IBM Plex Mono", monospace;
          font-size: 9px;
          color: var(--ink-soft);
          margin-top: 6px;
        }

        @media (max-width: 640px) {
          .details-grid {
            grid-template-columns: 1fr;
          }
          .dash-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }
        }
      `}</style>
    </>
  );
}
