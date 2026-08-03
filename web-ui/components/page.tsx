import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { type ReactNode, useEffect } from "react";
import { useConfig } from "@/components/config-context";
import { LoadingZone } from "@/components/loading-zone";

export interface PageProps {
  title: string;
  /** Hide the visible heading but still set the document title. */
  hideHeading?: boolean;
  /** Slot rendered to the right of the heading (actions, filters). */
  headerRight?: ReactNode;
  loading?: boolean;
  error?: unknown;
  children?: ReactNode;
}

/** Standard page shell: document title, heading row, loading state. */
export function Page({ title, hideHeading, headerRight, loading, error, children }: PageProps) {
  const { me } = useConfig();

  useEffect(() => {
    document.title = `${title} · ${me.site.title}`;
  }, [title, me.site.title]);

  return (
    <Stack spacing={2}>
      {!hideHeading && (
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 1,
          }}
        >
          <Typography variant="h4" component="h1">
            {title}
          </Typography>
          {headerRight}
        </Box>
      )}
      <LoadingZone loading={loading ?? false} error={error}>
        {children}
      </LoadingZone>
    </Stack>
  );
}
