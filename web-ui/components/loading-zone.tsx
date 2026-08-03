import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import type { ReactNode } from "react";
import { toErrorMessage } from "@/lib/api";

export interface LoadingZoneProps {
  loading: boolean;
  error?: unknown;
  children?: ReactNode;
}

/** Wraps content that depends on async data. */
export function LoadingZone({ loading, error, children }: LoadingZoneProps) {
  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }
  if (error) {
    return <Alert severity="error">{toErrorMessage(error)}</Alert>;
  }
  return <>{children}</>;
}
