import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// All frontend source lives in web-ui/; tooling configs live at the repo
// root. In development the vite server is the only origin the browser
// talks to: backend paths are proxied to Django, so requests stay
// same-origin (no CSRF/CORS special-casing) and hot reload just works.
const DJANGO = "http://localhost:8000";

export default defineConfig({
  root: "web-ui",
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./web-ui", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": DJANGO,
      "/media": DJANGO,
      "/static": DJANGO,
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    manifest: true,
  },
});
