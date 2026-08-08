// frontend/types.ts

export interface OpenRole {
  title: string;
  link: string;
}

export interface CompanyReport {
  company_name: string;
  one_liner: string;
  tech_stack: string[];
  team_size: string;
  key_people: string[];
  funding: string;
  recent_news: string[];
  open_roles: OpenRole[];
  pain_points: string[];
  fit_score: number;
  fit_reasoning: string;
  sources: string[];
}

export interface TopCompany {
  name: string;
  count: number;
}

export interface DailyActivity {
  date: string;
  count: number;
}

export interface StatsResponse {
  total_searches: number;
  unique_sessions: number;
  success_rate: number;
  searches_last_7_days: number;
  searches_last_30_days: number;
  top_companies: TopCompany[];
  // detailed fields (present when ?detailed=true)
  searches_prev_7_days?: number;
  daily_activity?: DailyActivity[];
  byok_count?: number;
  free_count?: number;
  avg_duration_ms?: number;
}
