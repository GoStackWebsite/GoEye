import { clearToken, getToken } from "./auth";
import { API_URL } from "./config";

export const LOGIN_PATH = "/login";

// Envelope returned by every backend endpoint
export interface ApiResponse<T> {
  success: boolean;
  message: string | null;
  data: T | null;
}

// Error thrown when the backend answers success=false or cannot be reached; message is safe to show
export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

/** Call the backend and return the envelope's data, or throw ApiError with the backend's message. */
export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError("Cannot reach the server", 0);
  }

  const body = (await response.json().catch(() => null)) as ApiResponse<T> | null;
  if (response.status === 401 && token) {
    clearToken();
    window.location.assign(LOGIN_PATH);
  }
  if (!response.ok || !body?.success) {
    throw new ApiError(body?.message ?? `Request failed (${response.status})`, response.status);
  }
  return body.data as T;
}
