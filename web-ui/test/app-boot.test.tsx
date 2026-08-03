import { afterEach, expect, test } from "bun:test";
import { render, screen } from "@testing-library/react";
import { App } from "@/app";
import { bootPayload, mockApi, ok } from "@/test/helpers";

let restore: (() => void) | null = null;

afterEach(() => {
  restore?.();
  restore = null;
  window.history.pushState({}, "", "/");
});

test("boots and renders the site title", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": ok(bootPayload()),
  }));
  render(<App />);
  expect(await screen.findByText("Test Kegbot")).toBeTruthy();
});

test("members-only site shows the login interstitial to anonymous users", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": ok(bootPayload({ site: { privacy: "members" } as never })),
  }));
  render(<App />);
  expect(await screen.findByText("Members only")).toBeTruthy();
  expect(screen.getByText("Log in")).toBeTruthy();
});

test("staff-only site blocks a logged-in non-staff member", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": ok(
      bootPayload({
        site: { privacy: "staff" } as never,
        user: {
          id: 2,
          username: "alice",
          email: "a@example.com",
          display_name: "alice",
          is_staff: false,
          is_active: true,
          picture: null,
        } as never,
      }),
    ),
  }));
  render(<App />);
  expect(await screen.findByText("Staff only")).toBeTruthy();
});

test("setup-required responses render the setup notice", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": { status: 403, body: { error: "setup_required" } },
  }));
  render(<App />);
  expect(await screen.findByText(/needs to be set up/)).toBeTruthy();
});
