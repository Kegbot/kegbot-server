import type { Me } from "@/api";

export interface MockResponse {
  status: number;
  body: unknown;
}

type Handler = MockResponse | ((request: Request) => MockResponse);

/**
 * Replaces global fetch with a route-table mock. Keys are
 * "METHOD /path"; values are responses or request handlers.
 * Returns a restore function.
 */
export function mockApi(handlers: Record<string, Handler>) {
  const originalFetch = globalThis.fetch;
  const seen: string[] = [];

  const mocked = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const request = input instanceof Request ? input : new Request(input, init);
    const path = new URL(request.url, "http://localhost").pathname;
    const key = `${request.method.toUpperCase()} ${path}`;
    seen.push(key);
    const handler = handlers[key];
    if (handler === undefined) {
      throw new Error(`Unmocked request: ${key}`);
    }
    const { status, body } = typeof handler === "function" ? handler(request) : handler;
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };

  globalThis.fetch = mocked as typeof fetch;
  return {
    seen,
    restore: () => {
      globalThis.fetch = originalFetch;
    },
  };
}

export function ok(body: unknown): MockResponse {
  return { status: 200, body };
}

export function bootPayload(overrides: Partial<Me> = {}): Me {
  return {
    user: null,
    site: {
      server_version: "2.0.0",
      title: "Test Kegbot",
      privacy: "public",
      registration_mode: "public",
      volume_display_units: "imperial",
      temperature_display_units: "f",
      timezone: "UTC",
      session_timeout_minutes: 180,
      enable_sensing: true,
      enable_users: true,
      google_analytics_id: null,
      background_image: null,
      ...(overrides.site ?? {}),
    },
    can_invite: true,
    have_sessions: true,
    sso_login_url: "",
    sso_logout_url: "",
    plugins: [{ short_name: "webhook", name: "Web Hooks" }],
    ...overrides,
  } as Me;
}
