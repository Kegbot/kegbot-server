import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import { statusRetrieve } from "@/api-client";
import { EmptyState } from "@/components/empty-state";
import { EventTimeline } from "@/components/event-timeline";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { TapCardLive } from "@/components/tap-card-live";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

export function HomeView() {
  const status = useAsyncData(() => unwrap(statusRetrieve()), { pollMs: 10_000 });

  return (
    <Page title="Home" hideHeading loading={status.loading} error={status.error}>
      {status.data && (
        <Grid container spacing={4}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Section label="On tap">
              <Stack spacing={2}>
                {status.data.taps.length === 0 && (
                  <EmptyState
                    title="No taps configured."
                    hint="Admins can add taps under Admin → Taps."
                  />
                )}
                {status.data.taps.map((tap) => (
                  <TapCardLive key={tap.id} tap={tap} />
                ))}
              </Stack>
            </Section>
          </Grid>
          <Grid size={{ xs: 12, md: 7 }}>
            <Section label="Recent activity">
              <EventTimeline events={status.data.events} />
            </Section>
          </Grid>
        </Grid>
      )}
    </Page>
  );
}
