import { afterEach } from "bun:test";
import { GlobalRegistrator } from "@happy-dom/global-registrator";

GlobalRegistrator.register({ url: "http://localhost/" });

// Registered here (after happy-dom) so every test file gets DOM cleanup.
const { cleanup } = await import("@testing-library/react");
afterEach(cleanup);
