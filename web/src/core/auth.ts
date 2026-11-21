const TOKEN_KEY = "goeye.token";

// Storage can be unavailable (private mode, blocked site data); the app then simply asks for a login again.
export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // not persisted: the session lasts until the page is reloaded
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // nothing stored
  }
}
