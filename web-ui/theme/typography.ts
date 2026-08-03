import type { ThemeOptions } from "@mui/material/styles";

/**
 * Type system: IBM Plex Sans for UI text, IBM Plex Mono for anything
 * data-like — numerals, eyebrow labels, the wordmark. The mono face is
 * the personality of the app; use it deliberately, not everywhere.
 */

export const BODY_FONT = '"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif';
export const MONO_FONT = '"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace';

export const typography: ThemeOptions["typography"] = {
  fontFamily: BODY_FONT,
  h1: { fontWeight: 600, fontSize: "2.5rem", letterSpacing: "-0.02em" },
  h2: { fontWeight: 600, fontSize: "2.125rem", letterSpacing: "-0.015em" },
  h3: { fontWeight: 600, fontSize: "1.75rem", letterSpacing: "-0.01em" },
  // Page titles.
  h4: { fontWeight: 600, fontSize: "1.625rem", letterSpacing: "-0.01em" },
  h5: { fontWeight: 600, fontSize: "1.25rem" },
  // Card headers.
  h6: { fontWeight: 600, fontSize: "1rem" },
  subtitle1: { fontWeight: 600 },
  subtitle2: { fontWeight: 600, fontSize: "0.8125rem" },
  body1: { fontSize: "0.9375rem" },
  body2: { fontSize: "0.875rem" },
  button: { fontWeight: 600, textTransform: "none", letterSpacing: "0.01em" },
  // Eyebrow/section labels: mono, uppercase, tracked out.
  overline: {
    fontFamily: MONO_FONT,
    fontWeight: 600,
    fontSize: "0.6875rem",
    letterSpacing: "0.12em",
    lineHeight: 2,
  },
  caption: { fontSize: "0.75rem" },
};
