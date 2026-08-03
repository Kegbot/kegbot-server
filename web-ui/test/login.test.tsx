import { afterEach, expect, test } from "bun:test";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { App } from "@/app";
import { bootPayload, mockApi, ok } from "@/test/helpers";

let restore: (() => void) | null = null;

afterEach(() => {
  restore?.();
  restore = null;
  window.history.pushState({}, "", "/");
});

test("failed login surfaces the server error", async () => {
  window.history.pushState({}, "", "/accounts/login");
  ({ restore } = mockApi({
    "GET /api/users/me": ok(bootPayload()),
    "POST /api/auth/login": {
      status: 400,
      body: { non_field_errors: ["Incorrect username/password"] },
    },
  }));
  render(<App />);

  const username = await screen.findByLabelText(/Username/);
  fireEvent.change(username, { target: { value: "alice" } });
  fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "nope" } });
  fireEvent.click(screen.getByRole("button", { name: "Log in" }));

  expect(await screen.findByText("Incorrect username/password")).toBeTruthy();
});

test("successful login refreshes the boot payload", async () => {
  window.history.pushState({}, "", "/accounts/login");
  const loggedOut = bootPayload();
  const loggedIn = bootPayload({
    user: {
      id: 2,
      username: "alice",
      email: "a@example.com",
      display_name: "Alice",
      is_staff: false,
      is_active: true,
      picture: null,
    } as never,
  });
  let bootCalls = 0;
  ({ restore } = mockApi({
    "GET /api/users/me": () => {
      bootCalls++;
      return ok(bootCalls === 1 ? loggedOut : loggedIn);
    },
    "POST /api/auth/login": ok(loggedIn.user),
  }));
  render(<App />);

  const username = await screen.findByLabelText(/Username/);
  fireEvent.change(username, { target: { value: "alice" } });
  fireEvent.change(screen.getByLabelText(/Password/), { target: { value: "pw" } });
  fireEvent.click(screen.getByRole("button", { name: "Log in" }));

  // After login + refresh, the login view redirects home.
  await waitFor(() => expect(window.location.pathname).toBe("/"));
  expect(bootCalls).toBeGreaterThanOrEqual(2);
});
