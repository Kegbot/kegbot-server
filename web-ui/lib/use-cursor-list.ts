import { useCallback, useEffect, useRef, useState } from "react";

export interface CursorPage<T> {
  next?: string | null;
  results?: T[];
}

export interface CursorList<T> {
  items: T[];
  loading: boolean;
  loadingMore: boolean;
  error: unknown;
  hasMore: boolean;
  loadMore: () => void;
  reload: () => void;
}

function cursorFromUrl(next: string | null | undefined): string | undefined {
  if (!next) {
    return undefined;
  }
  try {
    return new URL(next, window.location.origin).searchParams.get("cursor") ?? undefined;
  } catch {
    return undefined;
  }
}

/**
 * Incrementally loads a cursor-paginated endpoint ("load more" style).
 * Pass `deps` for filter values that should reset and refetch the list.
 */
export function useCursorList<T>(
  fetchPage: (cursor?: string) => Promise<CursorPage<T>>,
  deps: unknown[] = [],
): CursorList<T> {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [nextCursor, setNextCursor] = useState<string | undefined>(undefined);
  const [hasMore, setHasMore] = useState(false);
  const generation = useRef(0);
  const fetchRef = useRef(fetchPage);
  fetchRef.current = fetchPage;

  const loadFirst = useCallback(async () => {
    const requestId = ++generation.current;
    setLoading(true);
    setError(null);
    try {
      const page = await fetchRef.current(undefined);
      if (generation.current === requestId) {
        setItems(page.results ?? []);
        const cursor = cursorFromUrl(page.next);
        setNextCursor(cursor);
        setHasMore(Boolean(cursor));
      }
    } catch (e) {
      if (generation.current === requestId) {
        setError(e);
      }
    } finally {
      if (generation.current === requestId) {
        setLoading(false);
      }
    }
  }, []);

  const loadMore = useCallback(async () => {
    if (!nextCursor) {
      return;
    }
    const requestId = generation.current;
    setLoadingMore(true);
    try {
      const page = await fetchRef.current(nextCursor);
      if (generation.current === requestId) {
        setItems((existing) => [...existing, ...(page.results ?? [])]);
        const cursor = cursorFromUrl(page.next);
        setNextCursor(cursor);
        setHasMore(Boolean(cursor));
      }
    } catch (e) {
      if (generation.current === requestId) {
        setError(e);
      }
    } finally {
      setLoadingMore(false);
    }
  }, [nextCursor]);

  useEffect(() => {
    void loadFirst();
  }, [loadFirst, ...deps]);

  return {
    items,
    loading,
    loadingMore,
    error,
    hasMore,
    loadMore: () => void loadMore(),
    reload: () => void loadFirst(),
  };
}
