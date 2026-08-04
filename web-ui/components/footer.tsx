import Box from "@mui/material/Box";
import MuiLink from "@mui/material/Link";
import Typography from "@mui/material/Typography";

/** Quiet site footer. */
export function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        mt: "auto",
        py: 2,
        textAlign: "center",
        bgcolor: "background.paper",
        borderTop: 1,
        borderColor: "divider",
      }}
    >
      <Typography variant="caption" color="text.secondary">
        Powered by{" "}
        <MuiLink
          href="https://kegbot.org"
          target="_blank"
          rel="noopener"
          color="inherit"
          underline="hover"
        >
          Kegbot
        </MuiLink>
      </Typography>
    </Box>
  );
}
