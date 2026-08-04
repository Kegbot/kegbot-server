import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
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
import { sessionArchiveCrumbs, sessionTitle } from "@/views/sessions/session-list-view";

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
  const started = session.data ? new Date(session.data.start_time) : null;

  return (
    <Page
      title={session.data ? sessionTitle(session.data) : `Session #${sessionId}`}
      breadcrumbs={
        started
          ? sessionArchiveCrumbs(
              started.getFullYear(),
              started.getMonth() + 1,
              started.getDate(),
              `Session #${sessionId}`,
            )
          : undefined
      }
      eyebrow={`Session #${sessionId}`}
      meta={
        session.data && (
          <>
            {formatDateTime(session.data.start_time)} — {formatDateTime(session.data.end_time)} ·{" "}
            {volume(session.data.volume_ml ?? 0)} poured
          </>
        )
      }
      width="content"
      loading={session.loading}
      error={session.error}
    >
      {session.data && (
        <Stack spacing={4}>
          {stats?.volume_by_drinker && Object.keys(stats.volume_by_drinker).length > 0 && (
            <Section label="Drinkers">
              <Box sx={{ maxWidth: 560 }}>
                <VolumeByDrinkerChart data={stats.volume_by_drinker} />
              </Box>
            </Section>
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
