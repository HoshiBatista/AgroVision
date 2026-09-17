import axios from "axios";
import type {
  AuthUser,
  ConnectRtspStream,
  DashboardSnapshot,
  DemoManifest,
  ImagePrediction,
  ModelInfo,
  SessionRecord,
  Stream,
  TokenPair,
  VideoPrediction,
} from "./types";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const ACCESS_KEY = "agrovision_access";
const REFRESH_KEY = "agrovision_refresh";

export const tokenStore = {
  access: () => localStorage.getItem(ACCESS_KEY),
  refresh: () => localStorage.getItem(REFRESH_KEY),
  set: (pair: TokenPair) => {
    localStorage.setItem(ACCESS_KEY, pair.access_token);
    localStorage.setItem(REFRESH_KEY, pair.refresh_token);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = tokenStore.access();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function register(email: string, password: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/v1/auth/register", { email, password });
  tokenStore.set(data);
  return data;
}

export async function login(email: string, password: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>("/v1/auth/login", { email, password });
  tokenStore.set(data);
  return data;
}

export async function fetchMe(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>("/v1/auth/me");
  return data;
}

export async function fetchModelInfo(): Promise<ModelInfo> {
  const { data } = await api.get<ModelInfo>("/v1/model-info");
  return data;
}

export async function fetchDemoManifest(): Promise<DemoManifest> {
  const { data } = await api.get<DemoManifest>("/demo-media/manifest.json");
  return data;
}

export async function predictImage(file: File): Promise<ImagePrediction> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<ImagePrediction>("/v1/predictions", form);
  return data;
}

export async function predictVideo(file: File): Promise<VideoPrediction> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<VideoPrediction>("/v1/predictions/video", form);
  return data;
}

export async function listStreams(): Promise<Stream[]> {
  const { data } = await api.get<Stream[]>("/v1/streams");
  return data;
}

export async function connectRtspStream(payload: ConnectRtspStream): Promise<Stream> {
  const { data } = await api.post<Stream>("/v1/streams", payload);
  return data;
}

export async function disconnectRtspStream(streamId: string): Promise<void> {
  await api.delete(`/v1/streams/${streamId}`);
}

export async function updateModelThreshold(confidenceThreshold: number): Promise<ModelInfo> {
  const { data } = await api.patch<ModelInfo>("/v1/model-threshold", {
    confidence_threshold: confidenceThreshold,
  });
  return data;
}

export async function fetchDashboard(): Promise<DashboardSnapshot> {
  const { data } = await api.get<DashboardSnapshot>("/v1/dashboard");
  return data;
}

export async function listSessions(): Promise<SessionRecord[]> {
  const { data } = await api.get<SessionRecord[]>("/v1/reports/sessions");
  return data;
}

export function streamMjpegUrl(streamId: string): string {
  return `${API_URL}/v1/streams/${streamId}/mjpeg`;
}

export function dashboardWsUrl(): string {
  const url = new URL(`${API_URL}/v1/dashboard/ws`, window.location.origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
}

export function mediaUrl(path: string): string {
  return path.startsWith("http") ? path : `${API_URL}${path}`;
}

export async function exportReport(format: "csv" | "pdf"): Promise<void> {
  const { data } = await api.get(`/v1/reports/export.${format}`, { responseType: "blob" });
  const url = URL.createObjectURL(data as Blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `agrovision_sessions.${format}`;
  anchor.click();
  URL.revokeObjectURL(url);
}
