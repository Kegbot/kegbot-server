import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  // The ./ prefix matters: a bare "a/b" path parses as a Hey API
  // platform shorthand and crashes the generator.
  input: "./web-ui/schema.yaml",
  output: "web-ui/api-client",
  plugins: ["@hey-api/client-fetch"],
});
