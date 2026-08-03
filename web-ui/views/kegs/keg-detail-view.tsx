import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useParams } from "react-router";
import { drinksList, kegsRetrieve, kegsStatsRetrieve } from "@/api-client";
import { VolumeByDrinkerChart } from "@/components/charts/volume-by-drinker-chart";
import { DrinkList } from "@/components/drink-list";
import { KegProgress } from "@/components/keg-progress";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { SessionVolumeList } from "@/components/session-volume-list";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { asStats } from "@/lib/stats";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";
import { kegStatusChip } from "@/views/kegs/keg-list-view";

export function KegDetailView() {
  const params = useParams();
  const kegId = Number(params.id);
  const { volume } = useFormatters();

  const keg = useAsyncData(() => unwrap(kegsRetrieve({ path: { id: kegId } })), {
    deps: [kegId],
  });
  const stats = useAsyncData(
    async () => asStats(await unwrap(kegsStatsRetrieve({ path: { id: kegId } }))),
    { deps: [kegId] },
  );
  const drinks = useCursorList(
    (cursor) => unwrap(drinksList({ query: { keg: kegId, cursor } })),
    [kegId],
  );

  const beverage = keg.data?.beverage;
  const metadata = beverage
    ? [beverage.producer.name, beverage.style].filter(Boolean).join(" · ")
    : "";

  return (
    <Page
      title={beverage?.name ?? `Keg #${kegId}`}
      eyebrow={`Keg #${kegId}`}
      meta={
        keg.data && (
          <>
            {metadata}
            {metadata && " · "}first tapped {formatDate(keg.data.start_time)}
          </>
        )
      }
      headerRight={keg.data && kegStatusChip(keg.data)}
      width="content"
      loading={keg.loading}
      error={keg.error}
    >
      {keg.data && (
        <Stack spacing={4}>
          {keg.data.description && <Typography>{keg.data.description}</Typography>}
          <Grid container spacing={4}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Section label="Fill">
                <Stack spacing={1}>
                  <KegProgress keg={keg.data} />
                  <Typography variant="body2" color="text.secondary">
                    {volume(keg.data.served_volume_ml)} served
                    {(keg.data.spilled_ml ?? 0) > 0
                      ? ` · ${volume(keg.data.spilled_ml ?? 0)} spilled`
                      : ""}
                  </Typography>
                </Stack>
              </Section>
            </Grid>
            {stats.data?.volume_by_drinker &&
              Object.keys(stats.data.volume_by_drinker).length > 0 && (
                <Grid size={{ xs: 12, md: 6 }}>
                  <Section label="Top drinkers">
                    <VolumeByDrinkerChart data={stats.data.volume_by_drinker} limit={5} />
                  </Section>
                </Grid>
              )}
          </Grid>
          {stats.data?.volume_by_session && (
            <Section label="Sessions">
              <SessionVolumeList volumeBySession={stats.data.volume_by_session} />
            </Section>
          )}
          <Section label="Drinks">
            <Stack spacing={1}>
              <DrinkList drinks={drinks.items} hideKeg />
              <LoadMoreButton list={drinks} />
            </Stack>
          </Section>
        </Stack>
      )}
    </Page>
  );
}
