const API_BASE = "http://127.0.0.1:8008";

// --- Types -------------------------------------------------------------------

export interface Experience {
  id: number;
  company: string;
  role: string;
  location: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
}

export interface ExperienceInput {
  company: string;
  role: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
}

export interface Education {
  id: number;
  institution: string;
  degree: string;
  field_of_study: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
}

export interface EducationInput {
  institution: string;
  degree: string;
  field_of_study?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
}

export interface Skill {
  id: number;
  name: string;
  category: string | null;
  proficiency: number | null;
}

export interface SkillInput {
  name: string;
  category?: string | null;
  proficiency?: number | null;
}

export interface Link {
  id: number;
  name: string;
  url: string;
}

export interface LinkInput {
  name: string;
  url: string;
}

export interface Project {
  id: number;
  name: string;
  link: string | null;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
}

export interface ProjectInput {
  name: string;
  link?: string | null;
  description?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  city: string | null;
  state: string | null;
  headline: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
  experiences: Experience[];
  educations: Education[];
  skills: Skill[];
  links: Link[];
  projects: Project[];
}

export interface UserProfileInput {
  full_name: string;
  email: string;
  phone?: string | null;
  city?: string | null;
  state?: string | null;
  headline?: string | null;
  summary?: string | null;
}

export interface AtsCheck {
  name: string;
  passed: boolean;
  detail?: string;
}

export interface AtsResult {
  passed: boolean;
  checks: AtsCheck[];
}

export interface ResumeGenerateResult {
  docx_path: string;
  pdf_path: string | null;
  libreoffice_available: boolean;
  docx_ats: AtsResult;
  pdf_ats: AtsResult | null;
}

// --- Helpers -----------------------------------------------------------------

async function _req<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (res.status === 204) return undefined as T;
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${init?.method ?? "GET"} ${url} failed (${res.status}): ${detail}`);
  }
  return res.json();
}

// --- Profile -----------------------------------------------------------------

export async function getProfile(): Promise<UserProfile | null> {
  const res = await fetch(`${API_BASE}/api/profile`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function saveProfile(input: UserProfileInput): Promise<UserProfile> {
  return _req<UserProfile>(`${API_BASE}/api/profile`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

// --- Experience --------------------------------------------------------------

export async function createExperience(input: ExperienceInput): Promise<Experience> {
  return _req<Experience>(`${API_BASE}/api/profile/experiences`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function updateExperience(id: number, input: ExperienceInput): Promise<Experience> {
  return _req<Experience>(`${API_BASE}/api/profile/experiences/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteExperience(id: number): Promise<void> {
  await _req<void>(`${API_BASE}/api/profile/experiences/${id}`, { method: "DELETE" });
}

// --- Education ---------------------------------------------------------------

export async function createEducation(input: EducationInput): Promise<Education> {
  return _req<Education>(`${API_BASE}/api/profile/educations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function updateEducation(id: number, input: EducationInput): Promise<Education> {
  return _req<Education>(`${API_BASE}/api/profile/educations/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteEducation(id: number): Promise<void> {
  await _req<void>(`${API_BASE}/api/profile/educations/${id}`, { method: "DELETE" });
}

// --- Skill -------------------------------------------------------------------

export async function createSkill(input: SkillInput): Promise<Skill> {
  return _req<Skill>(`${API_BASE}/api/profile/skills`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function updateSkill(id: number, input: SkillInput): Promise<Skill> {
  return _req<Skill>(`${API_BASE}/api/profile/skills/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteSkill(id: number): Promise<void> {
  await _req<void>(`${API_BASE}/api/profile/skills/${id}`, { method: "DELETE" });
}

// --- Link --------------------------------------------------------------------

export async function createLink(input: LinkInput): Promise<Link> {
  return _req<Link>(`${API_BASE}/api/profile/links`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteLink(id: number): Promise<void> {
  await _req<void>(`${API_BASE}/api/profile/links/${id}`, { method: "DELETE" });
}

// --- Project -----------------------------------------------------------------

export async function createProject(input: ProjectInput): Promise<Project> {
  return _req<Project>(`${API_BASE}/api/profile/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export async function deleteProject(id: number): Promise<void> {
  await _req<void>(`${API_BASE}/api/profile/projects/${id}`, { method: "DELETE" });
}

// --- Resume / AI -------------------------------------------------------------

export async function enhanceSummary(raw_summary: string): Promise<string> {
  const res = await _req<{ enhanced_summary: string }>(`${API_BASE}/api/resume/enhance-summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_summary }),
  });
  return res.enhanced_summary;
}

export async function generateResume(): Promise<ResumeGenerateResult> {
  return _req<ResumeGenerateResult>(`${API_BASE}/api/resume/generate`, { method: "POST" });
}

export function resumeDownloadUrl(fmt: "docx" | "pdf"): string {
  return `${API_BASE}/api/resume/download/${fmt}`;
}