import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import { Link, useLocation } from "react-router";
import { useConfig } from "@/components/config-context";
import { useCurrentUser } from "@/components/current-user-context";

/**
 * Enforces the site privacy setting client-side (the API enforces it
 * server-side): members-only sites require login, staff-only sites
 * require a staff account.
 */
export function PrivacyGate({ children }: { children: ReactNode }) {
  const { me } = useConfig();
  const { user } = useCurrentUser();
  const location = useLocation();

  const privacy = me.site.privacy;
  const allowed =
    privacy === "public" || (privacy === "members" && user !== null) || user?.is_staff === true;

  if (allowed) {
    return <>{children}</>;
  }

  const needsLogin = user === null;
  return (
    <Paper
      sx={{
        p: 4,
        mt: 4,
        mx: "auto",
        maxWidth: 480,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 2,
        textAlign: "center",
      }}
    >
      <LockOutlinedIcon color="action" sx={{ fontSize: 48 }} />
      <Typography variant="h5">{privacy === "staff" ? "Staff only" : "Members only"}</Typography>
      <Typography color="text.secondary">
        {privacy === "staff"
          ? "This site is only viewable by staff accounts."
          : "You must log in to view this site."}
      </Typography>
      {needsLogin && (
        <Button
          component={Link}
          to={`/accounts/login?next=${encodeURIComponent(location.pathname)}`}
          variant="contained"
        >
          Log in
        </Button>
      )}
    </Paper>
  );
}
