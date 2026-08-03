import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { statusRetrieve } from "@/api";
import { EventTimeline } from "@/components/event-timeline";
import { Page } from "@/components/page";
import { TapCardLive } from "@/components/tap-card-live";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

export function HomeView() {
  const status = useAsyncData(() => unwrap(statusRetrieve()), { pollMs: 10_000 });

  return (
    <Page title="Home" hideHeading loading={status.loading} error={status.error}>
      {status.data && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Stack spacing={2}>
              <Typography variant="h5">On Tap</Typography>
              {status.data.taps.length === 0 && (
                <Typography color="text.secondary">No taps configured.</Typography>
              )}
              {status.data.taps.map((tap) => (
                <TapCardLive key={tap.id} tap={tap} />
              ))}
            </Stack>
          </Grid>
          <Grid size={{ xs: 12, md: 7 }}>
            <Stack spacing={2}>
              <Typography variant="h5">Recent Activity</Typography>
              <EventTimeline events={status.data.events} />
            </Stack>
          </Grid>
        </Grid>
      )}
    </Page>
  );
}
