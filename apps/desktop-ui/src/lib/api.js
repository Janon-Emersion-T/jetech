const fallbackUrl = "http://127.0.0.1:8000";

async function resolveBaseUrl() {
  try {
    const desktop = window.jarvisDesktop;
    if (desktop?.environment) {
      const env = await desktop.environment();
      return env.brainApiUrl || fallbackUrl;
    }
  } catch (error) {
    console.warn("Failed to resolve desktop environment", error);
  }
  return fallbackUrl;
}

export async function apiGet(path) {
  const baseUrl = await resolveBaseUrl();
  const response = await fetch(`${baseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`GET ${path} failed with status ${response.status}`);
  }
  return response.json();
}

export async function apiPost(path, payload) {
  const baseUrl = await resolveBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`POST ${path} failed with status ${response.status}`);
  }
  return response.json();
}
