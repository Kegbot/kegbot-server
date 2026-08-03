import { expect, test } from "bun:test";
import { act, renderHook, waitFor } from "@testing-library/react";
import { useAsyncData } from "@/lib/use-async-data";

test("resolves data", async () => {
  const { result } = renderHook(() => useAsyncData(async () => 42));
  expect(result.current.loading).toBe(true);
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.data).toBe(42);
  expect(result.current.error).toBeNull();
});

test("captures errors", async () => {
  const boom = new Error("boom");
  const { result } = renderHook(() =>
    useAsyncData(async () => {
      throw boom;
    }),
  );
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.error).toBe(boom);
  expect(result.current.data).toBeNull();
});

test("reload refetches", async () => {
  let calls = 0;
  const { result } = renderHook(() =>
    useAsyncData(async () => {
      calls++;
      return calls;
    }),
  );
  await waitFor(() => expect(result.current.data).toBe(1));
  act(() => result.current.reload());
  await waitFor(() => expect(result.current.data).toBe(2));
});

test("disabled hook does not fetch", async () => {
  let calls = 0;
  renderHook(() =>
    useAsyncData(
      async () => {
        calls++;
        return calls;
      },
      { enabled: false },
    ),
  );
  await new Promise((resolve) => setTimeout(resolve, 10));
  expect(calls).toBe(0);
});
