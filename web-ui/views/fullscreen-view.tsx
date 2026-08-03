import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { useEffect, useState } from "react";
import { statusRetrieve } from "@/api-client";
import { useConfig } from "@/components/config-context";
import { EmptyState } from "@/components/empty-state";
import { EventTimeline } from "@/components/event-timeline";
import { LoadingZone } from "@/components/loading-zone";
import { Section } from "@/components/section";
import { TapCardLive } from "@/components/tap-card-live";
import { Wordmark } from "@/components/wordmark";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { MONO_FONT } from "@/theme/typography";

function Clock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 10_000);
    return () => clearInterval(interval);
  }, []);
  return (
    <Typography
      sx={{
        fontFamily: MONO_FONT,
        fontWeight: 600,
        fontSize: "1.5rem",
        letterSpacing: "0.06em",
        color: "text.secondary",
      }}
    >
      {now.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}
    </Typography>
  );
}

/**
 * Kiosk mode: always dark, oversized tap cards, live clock. Polls the
 * status endpoint and re-renders in place.
 */
export function FullscreenView() {
  const { me } = useConfig();
  const status = useAsyncData(() => unwrap(statusRetrieve()), { pollMs: 10_000 });

  useEffect(() => {
    document.title = me.site.title ?? "Kegbot";
  }, [me.site.title]);

  return (
    // Scoped dark scheme: kiosk screens are dark regardless of the
    // viewer preference.
    <Box
      data-color-scheme="dark"
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
        color: "text.primary",
        p: { xs: 2.5, md: 5 },
        display: "flex",
        flexDirection: "column",
        gap: 4,
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Wordmark siteTitle={me.site.title} />
        <Clock />
      </Box>
      <LoadingZone loading={status.loading} error={status.error}>
        {status.data && (
          <Grid container spacing={5} sx={{ flexGrow: 1 }}>
            <Grid size={{ xs: 12, lg: 8 }}>
              <Section label="On tap">
                {status.data.taps.length === 0 ? (
                  <EmptyState title="No taps configured." />
                ) : (
                  <Grid container spacing={3}>
                    {status.data.taps.map((tap) => (
                      <Grid key={tap.id} size={{ xs: 12, md: 6 }}>
                        <TapCardLive tap={tap} large />
                      </Grid>
                    ))}
                  </Grid>
                )}
              </Section>
            </Grid>
            <Grid size={{ xs: 12, lg: 4 }}>
              <Section label="Recent activity">
                <EventTimeline events={status.data.events.slice(0, 8)} />
              </Section>
            </Grid>
          </Grid>
        )}
      </LoadingZone>
    </Box>
  );
}
