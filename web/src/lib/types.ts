export interface CvProfile {
  area: string;
  is_tech: boolean;
  seniority: string;
  skills: string[];
  search_queries: string[];
  search_queries_en?: string[];
}

export interface JobResult {
  job_id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  modality?: string;
  description?: string;
  url: string;
  posted_at?: string;
  scraped_at?: string;
  similarity?: number;
  score?: number;
  matches?: string[];
  gaps?: string[];
  explicacion?: string;
  applied?: boolean;
}

export interface MatchRunResponse {
  cv_id: string;
  match_id: string;
  profile: CvProfile;
  results: JobResult[];
}
