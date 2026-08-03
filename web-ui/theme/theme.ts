import { createTheme } from "@mui/material/styles";
import { components } from "@/theme/components";
import { darkPalette, lightPalette } from "@/theme/palette";
import { typography } from "@/theme/typography";

/**
 * The Kegbot theme: cool neutral surfaces, one amber accent, IBM Plex
 * type with mono data accents. Light and dark schemes follow the system
 * by default; the nav switch persists a per-user override.
 */
export const theme = createTheme({
  cssVariables: {
    colorSchemeSelector: "data-color-scheme",
  },
  colorSchemes: {
    light: { palette: lightPalette },
    dark: { palette: darkPalette },
  },
  shape: {
    borderRadius: 10,
  },
  typography,
  components,
});
