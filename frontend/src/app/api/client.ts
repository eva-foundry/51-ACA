// EVA-STORY: ACA-05-026
/**
 * Base HTTP client for ACA API.
 * All API calls go through this function.
 * Credentials are included for session-cookie auth.
 * Throws an Error with the server response body on non-ok status.
 */

export const apiBase =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api";

export async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    credentials: "include",
  });

  if (!res.ok) {
    let body = "";
    try { body = await res.text(); } catch { /* ignore */ }
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }

  // 204 No Content -- return null-ish
  if (res.status === 204) {
    return undefined as unknown as T;
  }

  return res.json() as Promise<T>;
}

export const client = { http };
