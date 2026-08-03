import { client } from "@/api-client/client.gen";

/** DRF-style field errors: `{fieldName: ["message", ...]}`. */
export type FormErrors = Record<string, string[]>;

export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

// The generated client is configured once, at import time. All requests
// are same-origin (the vite dev server proxies /api to Django), so
// session-cookie auth plus the CSRF header is all we need.
client.setConfig({
  baseUrl: "/",
  credentials: "include",
});

client.interceptors.request.use((request) => {
  const token = getCsrfToken();
  if (token) {
    request.headers.set("X-CSRFToken", token);
  }
  return request;
});

/**
 * Awaits a generated-client call, returning `data` or throwing `error`
 * (the parsed response body — e.g. a DRF field-error object).
 */
export async function unwrap<D>(promise: Promise<{ data?: D; error?: unknown }>): Promise<D> {
  const { data, error } = await promise;
  if (error !== undefined) {
    throw error;
  }
  return data as D;
}

/**
 * Returns DRF field errors from a thrown API error, or null when the
 * error is not a field-validation failure.
 */
export function getFormErrors(error: unknown): FormErrors | null {
  if (!error || typeof error !== "object" || Array.isArray(error)) {
    return null;
  }
  const entries = Object.entries(error as Record<string, unknown>);
  if (entries.length === 0) {
    return null;
  }
  const result: FormErrors = {};
  for (const [field, value] of entries) {
    if (Array.isArray(value) && value.every((v) => typeof v === "string")) {
      result[field] = value;
    } else if (typeof value === "string") {
      result[field] = [value];
    } else {
      return null;
    }
  }
  return result;
}

/** Best-effort human-readable message from a thrown API error. */
export function toErrorMessage(error: unknown): string {
  if (typeof error === "string") {
    return error;
  }
  if (error && typeof error === "object") {
    const detail = (error as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    const formErrors = getFormErrors(error);
    if (formErrors) {
      const first = Object.values(formErrors)[0];
      if (first?.length) {
        return first[0];
      }
    }
    if (error instanceof Error) {
      return error.message;
    }
  }
  return "Something went wrong.";
}
