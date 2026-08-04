import MuiBreadcrumbs from "@mui/material/Breadcrumbs";
import MuiLink from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import { MONO_FONT } from "@/theme/typography";

export interface Crumb {
  label: string;
  /** Omit on the current (last) crumb. */
  to?: string;
}

/** Mono breadcrumb trail ("Sessions / 2026 / August / 3"). */
export function Breadcrumbs({ crumbs }: { crumbs: Crumb[] }) {
  return (
    <MuiBreadcrumbs
      separator="/"
      aria-label="breadcrumb"
      sx={{
        fontFamily: MONO_FONT,
        fontSize: "0.8125rem",
        "& .MuiBreadcrumbs-separator": { mx: 0.75, color: "text.secondary", opacity: 0.6 },
      }}
    >
      {crumbs.map((crumb) =>
        crumb.to ? (
          <MuiLink
            key={`${crumb.label}-${crumb.to}`}
            component={Link}
            to={crumb.to}
            underline="hover"
            color="text.secondary"
            sx={{ fontFamily: "inherit", fontSize: "inherit", fontWeight: 500 }}
          >
            {crumb.label}
          </MuiLink>
        ) : (
          <Typography
            key={crumb.label}
            component="span"
            sx={{ fontFamily: "inherit", fontSize: "inherit", fontWeight: 600 }}
            color="text.primary"
          >
            {crumb.label}
          </Typography>
        ),
      )}
    </MuiBreadcrumbs>
  );
}
