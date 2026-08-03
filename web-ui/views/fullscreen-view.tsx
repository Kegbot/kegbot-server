import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect } from "react";
import { statusRetrieve } from "@/api";
import { useConfig } from "@/components/config-context";
import { EventTimeline } from "@/components/event-timeline";
import { LoadingZone } from "@/components/loading-zone";
import { TapCardLive } from "@/components/tap-card-live";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

/**
 * Kiosk mode: full-bleed on-tap display that stays current by polling
 * (the old page reloaded itself; this just re-renders).
 */
export function FullscreenView() {
  const { me } = useConfig();
  const status = useAsyncData(() => unwrap(statusRetrieve()), { pollMs: 10_000 });

  useEffect(() => {
    document.title = me.site.title ?? "Kegbot";
  }, [me.site.title]);

  return (
    <Box sx={{ minHeight: "100vh", p: { xs: 2, md: 4 } }}>
      <Typography variant="h3" sx={{ mb: 3 }}>
        {me.site.title}
      </Typography>
      <LoadingZone loading={status.loading} error={status.error}>
        {status.data && (
          <Grid container spacing={4}>
            <Grid size={{ xs: 12, md: 7 }}>
              <Grid container spacing={3}>
                {status.data.taps.map((tap) => (
                  <Grid key={tap.id} size={{ xs: 12, sm: 6 }}>
                    <TapCardLive tap={tap} />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid size={{ xs: 12, md: 5 }}>
              <Stack spacing={2}>
                <Typography variant="h5">Recent Activity</Typography>
                <EventTimeline events={status.data.events.slice(0, 10)} />
              </Stack>
            </Grid>
          </Grid>
        )}
      </LoadingZone>
    </Box>
  );
}
