
export interface User {
  id: number;
  email: string;
  username: string;
  password_hash: string;
  created_at: string;
  is_verified: boolean;
  scan_limit?: number;
}

export interface Scan {
  id: number;
  user_id: number;
  target_url: string;
  status: "pending" | "running" | "completed" | "failed";
  started_at: string;
  finished_at?: string;
}

export interface ScanResult {
  id: number;
  scan_id: number;
  tool_used: "sqlmap" | "nmap" | "nikto";
  raw_output: string;
  ai_analysis?: string;
  severity: "low" | "medium" | "high" | "critical";
  vulnerability_type?: string;
  suggested_fix?: string;
}

export interface Report {
  id: number;
  scan_id: number;
  pdf_path: string;
  emailed: boolean;
}

export type AuthUser = Omit<User, 'password_hash'> & {
  token?: string;
  is_guest?: boolean;
};
