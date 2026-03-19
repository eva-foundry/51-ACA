export async function adminGet<T>(path: string, token: string): Promise<T> {
  const res = await fetch(path, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    throw new Error(`Admin API error: ${res.status}`);
  }
  return res.json();
}
