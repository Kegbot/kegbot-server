import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// All frontend source lives in web-ui/; tooling configs live at the repo
// root. In development the vite server is the only origin the browser
// talks to — http://localhost:8000 "just works": backend paths are
// proxied to Django (which `kegbot runserver` starts on 8001), so
// requests stay same-origin (no CSRF/CORS special-casing) and hot
// reload just works.
const DJANGO = "http://localhost:8001";

export default defineConfig(({ command }) => ({
  root: "web-ui",
  // Production assets are collected into Django's static tree and served
  // by WhiteNoise under /static/; the dev server serves from the root.
  base: command === "build" ? "/static/" : "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./web-ui", import.meta.url)),
    },
  },
  server: {
    port: 8000,
    // Segment-anchored regexes: a bare "/api" key is a prefix match and
    // would also capture source modules under /api-client/.
    //
    // changeOrigin must stay off (string shorthands turn it on): Django
    // must see the browser's Host so its CSRF origin check passes.
    proxy: {
      "^/api(?:/|$)": { target: DJANGO, changeOrigin: false },
      "^/media(?:/|$)": { target: DJANGO, changeOrigin: false },
      "^/static(?:/|$)": { target: DJANGO, changeOrigin: false },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    manifest: true,
  },
}));
