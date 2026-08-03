import { useCallback, useEffect, useRef, useState } from "react";

export interface AsyncData<T> {
  data: T | null;
  loading: boolean;
  error: unknown;
  reload: () => void;
}

export interface UseAsyncDataOptions {
  /** Refetch when these values change (like a useEffect deps array). */
  deps?: unknown[];
  /** Refresh this often; background refreshes do not toggle `loading`. */
  pollMs?: number;
  /** When false, nothing is fetched and state resets to loading. */
  enabled?: boolean;
}

/**
 * Minimal data-fetching hook: `{data, loading, error, reload}`.
 *
 * The fetcher may be an inline closure — its identity is not tracked.
 * Pass `deps` for values (route params, filters) that should trigger a
 * refetch when they change.
 */
export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  options: UseAsyncDataOptions = {},
): AsyncData<T> {
  const { deps = [], pollMs, enabled = true } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<unknown>(null);
  const generation = useRef(0);
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const load = useCallback(async (background: boolean) => {
    const requestId = ++generation.current;
    if (!background) {
      setLoading(true);
    }
    try {
      const result = await fetcherRef.current();
      if (generation.current === requestId) {
        setData(result);
        setError(null);
      }
    } catch (e) {
      if (generation.current === requestId) {
        setError(e);
      }
    } finally {
      if (generation.current === requestId && !background) {
        setLoading(false);
      }
    }
  }, []);

  const reload = useCallback(() => {
    void load(false);
  }, [load]);

  useEffect(() => {
    if (!enabled) {
      generation.current++;
      setData(null);
      setError(null);
      setLoading(true);
      return;
    }
    void load(false);
    if (!pollMs) {
      return;
    }
    const interval = setInterval(() => void load(true), pollMs);
    return () => clearInterval(interval);
  }, [enabled, load, pollMs, ...deps]);

  return { data, loading, error, reload };
}
