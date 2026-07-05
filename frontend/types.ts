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
