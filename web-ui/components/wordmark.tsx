import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { MONO_FONT } from "@/theme/typography";

/**
 * The Kegbot wordmark: mono, uppercase, tracked out, with an amber
 * tap-handle tick. Site title (when customized) rides alongside.
 */
export function Wordmark({ siteTitle }: { siteTitle?: string | null }) {
  const showSiteTitle = siteTitle && siteTitle.toLowerCase() !== "kegbot";
  return (
    <Stack direction="row" spacing={1.25} sx={{ alignItems: "center", minWidth: 0 }}>
      <Box
        aria-hidden
        sx={{
          width: 10,
          height: 18,
          borderRadius: "3px 3px 2px 2px",
          bgcolor: "primary.main",
          flexShrink: 0,
        }}
      />
      <Typography
        component="span"
        sx={{
          fontFamily: MONO_FONT,
          fontWeight: 600,
          fontSize: "0.9375rem",
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: "text.primary",
        }}
      >
        Kegbot
      </Typography>
      {showSiteTitle && (
        <Typography
          component="span"
          noWrap
          sx={{
            color: "text.secondary",
            fontSize: "0.9375rem",
            borderLeft: 1,
            borderColor: "divider",
            pl: 1.25,
          }}
        >
          {siteTitle}
        </Typography>
      )}
    </Stack>
  );
}
