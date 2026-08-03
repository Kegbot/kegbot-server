import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useParams } from "react-router";
import { drinksList, sessionsRetrieve } from "@/api-client";
import { VolumeByDrinkerChart } from "@/components/charts/volume-by-drinker-chart";
import { DrinkList } from "@/components/drink-list";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { asStats } from "@/lib/stats";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";
import { sessionTitle } from "@/views/sessions/session-list-view";

export function SessionDetailView() {
  const params = useParams();
  const sessionId = Number(params.id);
  const { volume } = useFormatters();

  const session = useAsyncData(() => unwrap(sessionsRetrieve({ path: { id: sessionId } })), {
    deps: [sessionId],
  });
  const drinks = useCursorList(
    (cursor) => unwrap(drinksList({ query: { session: sessionId, cursor } })),
    [sessionId],
  );

  const stats = session.data ? asStats(session.data.stats) : null;

  return (
    <Page
      title={session.data ? sessionTitle(session.data) : `Session #${sessionId}`}
      loading={session.loading}
      error={session.error}
    >
      {session.data && (
        <Stack spacing={3}>
          <Typography color="text.secondary">
            {formatDateTime(session.data.start_time)} — {formatDateTime(session.data.end_time)} ·{" "}
            {volume(session.data.volume_ml ?? 0)} poured
          </Typography>
          {stats?.volume_by_drinker && Object.keys(stats.volume_by_drinker).length > 0 && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 7 }}>
                <Card variant="outlined">
                  <CardHeader title="Drinkers" />
                  <CardContent>
                    <VolumeByDrinkerChart data={stats.volume_by_drinker} />
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          <Section label="Drinks">
            <Stack spacing={1}>
              <DrinkList drinks={drinks.items} />
              <LoadMoreButton list={drinks} />
            </Stack>
          </Section>
        </Stack>
      )}
    </Page>
  );
}
