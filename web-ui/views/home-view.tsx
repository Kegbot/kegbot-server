import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
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
        <Box sx={{ display: "flex", flexDirection: "column", gap: 5 }}>
          {/* The tap deck is the hero: what's pouring, and how much is left. */}
          <Section label="On tap">
            {status.data.taps.length === 0 ? (
              <EmptyState
                title="No taps configured."
                hint="Admins can add taps under Admin → Taps."
              />
            ) : (
              <Grid container spacing={2.5}>
                {status.data.taps.map((tap) => (
                  <Grid key={tap.id} size={{ xs: 12, sm: 6, lg: 4 }}>
                    <TapCardLive tap={tap} />
                  </Grid>
                ))}
              </Grid>
            )}
          </Section>
          <Section label="Recent activity">
            <Box sx={{ maxWidth: 680 }}>
              <EventTimeline events={status.data.events} />
            </Box>
          </Section>
        </Box>
      )}
    </Page>
  );
}
