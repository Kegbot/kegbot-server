import type { Theme, ThemeOptions } from "@mui/material/styles";
import { MONO_FONT } from "@/theme/typography";

/** Component defaults and overrides shared by both color schemes. */
export const components: ThemeOptions["components"] = {
  MuiButton: {
    defaultProps: {
      disableElevation: true,
    },
    styleOverrides: {
      root: {
        borderRadius: 8,
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      rounded: {
        borderRadius: 10,
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 10,
      },
    },
  },
  MuiCardHeader: {
    defaultProps: {
      slotProps: {
        title: { variant: "h6" },
        subheader: { variant: "body2" },
      },
    },
    styleOverrides: {
      root: {
        paddingBottom: 8,
      },
    },
  },
  MuiTableCell: {
    styleOverrides: {
      head: ({ theme }: { theme: Theme }) => ({
        fontFamily: MONO_FONT,
        fontSize: "0.6875rem",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.08em",
        color: (theme.vars ?? theme).palette.text.secondary,
        whiteSpace: "nowrap",
      }),
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        fontWeight: 600,
      },
    },
  },
  MuiTab: {
    styleOverrides: {
      root: {
        textTransform: "none",
        fontWeight: 600,
      },
    },
  },
  MuiLink: {
    defaultProps: {
      underline: "hover",
    },
    styleOverrides: {
      root: {
        fontWeight: 500,
      },
    },
  },
  MuiAvatar: {
    styleOverrides: {
      // Letter-fallback avatars wear the accent, quietly.
      colorDefault: ({ theme }: { theme: Theme }) => ({
        backgroundColor: (theme.vars ?? theme).palette.primary.main,
        color: (theme.vars ?? theme).palette.primary.contrastText,
        fontWeight: 600,
      }),
    },
  },
  MuiAppBar: {
    defaultProps: {
      elevation: 0,
      color: "transparent",
    },
  },
  MuiListSubheader: {
    styleOverrides: {
      root: ({ theme }: { theme: Theme }) => ({
        fontFamily: MONO_FONT,
        fontSize: "0.65rem",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.12em",
        lineHeight: "2.6",
        color: (theme.vars ?? theme).palette.text.secondary,
        backgroundColor: "transparent",
      }),
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        fontSize: "0.75rem",
      },
    },
  },
};
