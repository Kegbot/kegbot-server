/**
 * Kegbot palette: cool near-neutral surfaces with a single amber accent
 * ("precision instrument, warmly accented"). Chart series colors are
 * validated for contrast and CVD separation against each mode's
 * surface — change them only with revalidation.
 */

export const lightPalette = {
  primary: {
    main: "#96590E",
    light: "#C98833",
    dark: "#74450B",
    contrastText: "#FFFFFF",
  },
  secondary: {
    main: "#5C5A55",
    light: "#807E78",
    dark: "#403E3A",
    contrastText: "#FFFFFF",
  },
  success: { main: "#2F7D46" },
  warning: { main: "#A66A0E" },
  error: { main: "#C2402F" },
  info: { main: "#1878A0" },
  background: {
    default: "#F6F6F4",
    paper: "#FFFFFF",
  },
  text: {
    primary: "#1C1B18",
    secondary: "#605C54",
  },
  divider: "rgba(28, 27, 24, 0.12)",
};

export const darkPalette = {
  primary: {
    main: "#E29A3F",
    light: "#EDB56C",
    dark: "#B97921",
    contrastText: "#1A1206",
  },
  secondary: {
    main: "#8A867E",
    light: "#ABA79F",
    dark: "#6A665F",
    contrastText: "#131313",
  },
  success: { main: "#6FAF7C" },
  warning: { main: "#D89A3E" },
  error: { main: "#E07B6C" },
  info: { main: "#58A8C6" },
  background: {
    default: "#141311",
    paper: "#1D1B18",
  },
  text: {
    primary: "#EDEBE6",
    secondary: "#A6A299",
  },
  divider: "rgba(237, 235, 230, 0.12)",
};

/**
 * Chart series colors in fixed assignment order (amber, teal, hop
 * green, plum). Validated with the palette checker for both surfaces.
 */
export const CHART_SERIES_LIGHT = ["#B96A1B", "#1878A0", "#5F8A2C", "#9A4E86"];
export const CHART_SERIES_DARK = ["#D07E1F", "#2E8CB4", "#6FA032", "#B15E97"];
