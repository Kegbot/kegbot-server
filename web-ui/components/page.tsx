import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { type ReactNode, useEffect } from "react";
import { Breadcrumbs, type Crumb } from "@/components/breadcrumbs";
import { useConfig } from "@/components/config-context";
import { LoadingZone } from "@/components/loading-zone";

const WIDTHS = {
  /** Full container width: dashboards, tables. */
  wide: "none",
  /** Reading/detail pages. */
  content: "880px",
  /** Single-purpose forms. */
  narrow: "560px",
} as const;

export interface PageProps {
  title: string;
  /** Hide the visible heading but still set the document title. */
  hideHeading?: boolean;
  /** Mono label above the title ("KEG #12"). */
  eyebrow?: string;
  /** Breadcrumb trail above the title; replaces the eyebrow slot. */
  breadcrumbs?: Crumb[];
  /** Metadata line under the title; may contain links/chips. */
  meta?: ReactNode;
  /** Leading visual beside the title (an Avatar, usually). */
  avatar?: ReactNode;
  /** Slot to the right of the heading (actions, filters). */
  headerRight?: ReactNode;
  /** Content width intent. */
  width?: keyof typeof WIDTHS;
  loading?: boolean;
  error?: unknown;
  children?: ReactNode;
}

/**
 * Standard page shell: document title, one header anatomy
 * (eyebrow / avatar+title / meta / actions), loading state, and a
 * declared content width.
 */
export function Page({
  title,
  hideHeading,
  eyebrow,
  breadcrumbs,
  meta,
  avatar,
  headerRight,
  width = "wide",
  loading,
  error,
  children,
}: PageProps) {
  const { me } = useConfig();

  useEffect(() => {
    document.title = `${title} · ${me.site.title ?? "Kegbot"}`;
  }, [title, me.site.title]);

  return (
    <Stack spacing={3} sx={{ maxWidth: WIDTHS[width] }}>
      {!hideHeading && (
        <Box>
          {breadcrumbs ? (
            <Box sx={{ mb: 1 }}>
              <Breadcrumbs crumbs={breadcrumbs} />
            </Box>
          ) : (
            eyebrow && (
              <Typography variant="overline" color="text.secondary" component="div">
                {eyebrow}
              </Typography>
            )
          )}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 2,
            }}
          >
            <Stack direction="row" spacing={2} sx={{ alignItems: "center", minWidth: 0 }}>
              {avatar}
              <Box sx={{ minWidth: 0 }}>
                <Typography variant="h4" component="h1">
                  {title}
                </Typography>
                {meta && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    component="div"
                    sx={{ mt: 0.25 }}
                  >
                    {meta}
                  </Typography>
                )}
              </Box>
            </Stack>
            {headerRight}
          </Box>
        </Box>
      )}
      <LoadingZone loading={loading ?? false} error={error}>
        {children}
      </LoadingZone>
    </Stack>
  );
}
