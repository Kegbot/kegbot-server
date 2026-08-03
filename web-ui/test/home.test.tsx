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

const KEG = {
  id: 1,
  beverage: {
    id: 1,
    name: "Test IPA",
    producer: { id: 1, name: "Test Brewery" },
    style: "IPA",
  },
  keg_type: "half-barrel",
  served_volume_ml: 10000,
  full_volume_ml: 58673.9,
  spilled_ml: 0,
  start_time: "2026-08-01T00:00:00Z",
  end_time: "2026-08-01T00:00:00Z",
  status: "on_tap",
};

const STATUS = {
  site: bootPayload().site,
  taps: [
    {
      id: 1,
      name: "Main Tap",
      current_keg_id: 1,
      temperature_sensor_id: null,
      sort_order: 0,
      current_keg: KEG,
    },
  ],
  events: [
    {
      id: 42,
      kind: "drink_poured",
      time: new Date().toISOString(),
      user: {
        id: 2,
        username: "alice",
        display_name: "alice",
        is_staff: false,
        is_active: true,
        picture: null,
      },
      drink: {
        id: 7,
        ticks: 0,
        volume_ml: 400,
        time: new Date().toISOString(),
        duration: 4,
        user: null,
        keg: KEG,
        session_id: 3,
        shout: "cheers",
        picture: null,
      },
      keg: null,
      session: null,
    },
  ],
};

test("home renders taps and recent events", async () => {
  ({ restore } = mockApi({
    "GET /api/users/me": ok(bootPayload()),
    "GET /api/status": ok(STATUS),
  }));
  render(<App />);

  expect(await screen.findByText("Test IPA")).toBeTruthy();
  expect(screen.getByText("Main Tap")).toBeTruthy();
  expect(screen.getByText("alice")).toBeTruthy();
  expect(screen.getByText(/poured/)).toBeTruthy();
  expect(screen.getByText(/cheers/)).toBeTruthy();
});
