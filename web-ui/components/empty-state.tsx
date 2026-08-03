import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export interface EmptyStateProps {
  /** What there is none of ("No drinks yet."). */
  title: string;
  /** Optional direction: what would put something here. */
  hint?: string;
  /** Optional action (a button or link). */
  action?: ReactNode;
}

/** Quiet, consistent empty state for lists and tables. */
export function EmptyState({ title, hint, action }: EmptyStateProps) {
  return (
    <Box
      sx={{
        py: 4,
        px: 2,
        textAlign: "center",
        border: 1,
        borderStyle: "dashed",
        borderColor: "divider",
        borderRadius: 2,
      }}
    >
      <Typography color="text.secondary">{title}</Typography>
      {hint && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, opacity: 0.8 }}>
          {hint}
        </Typography>
      )}
      {action && <Box sx={{ mt: 1.5 }}>{action}</Box>}
    </Box>
  );
}
