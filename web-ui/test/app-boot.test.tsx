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

test("setup-required responses render the setup wizard", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": { status: 403, body: { error: "setup_required" } },
  }));
  render(<App />);
  expect(await screen.findByText("Welcome to Kegbot!")).toBeTruthy();
  expect(screen.getByText("Set up database")).toBeTruthy();
});

test("upgrade-required responses render the upgrade flow", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": { status: 403, body: { error: "upgrade_required" } },
    "GET /api/setup/status": {
      status: 200,
      body: {
        need_setup: false,
        need_upgrade: true,
        installed_version: "1.0.0",
        current_version: "2.0.0",
      },
    },
  }));
  render(<App />);
  expect(await screen.findByText("Upgrade required")).toBeTruthy();
  expect(await screen.findByText(/1\.0\.0/)).toBeTruthy();
});
