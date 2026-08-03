import { expect, test } from "bun:test";
import { splitResetParam } from "@/views/auth/password-reset-confirm-view";

test("splits uid and token", () => {
  expect(splitResetParam("MQ-abc123-def456")).toEqual({ uid: "MQ", token: "abc123-def456" });
});

test("uid may itself contain dashes", () => {
  expect(splitResetParam("M-Q-abc123-def456")).toEqual({ uid: "M-Q", token: "abc123-def456" });
});

test("rejects malformed values", () => {
  expect(splitResetParam("junk")).toBeNull();
  expect(splitResetParam("a-b")).toBeNull();
});
