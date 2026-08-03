import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export interface SectionProps {
  /** Eyebrow label; rendered mono-uppercase ("ON TAP"). */
  label: string;
  /** Slot on the right of the eyebrow row (actions, filters, counts). */
  action?: ReactNode;
  children: ReactNode;
}

/** Standard content section: mono eyebrow label over the content. */
export function Section({ label, action, children }: SectionProps) {
  return (
    <Stack spacing={1.5} component="section">
      <Box
        sx={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: 1,
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Typography variant="overline" color="text.secondary" component="h2">
          {label}
        </Typography>
        {action}
      </Box>
      {children}
    </Stack>
  );
}
