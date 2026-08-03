import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
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

  const title = keg.data ? keg.data.beverage.name : `Keg #${kegId}`;

  return (
    <Page title={title} loading={keg.loading} error={keg.error}>
      {keg.data && (
        <Stack spacing={3}>
          <Stack direction="row" spacing={2} sx={{ alignItems: "center", flexWrap: "wrap" }}>
            {kegStatusChip(keg.data)}
            <Typography color="text.secondary">
              {keg.data.beverage.producer.name}
              {keg.data.beverage.style ? ` · ${keg.data.beverage.style}` : ""} · first tapped{" "}
              {formatDate(keg.data.start_time)}
            </Typography>
          </Stack>
          {keg.data.description && <Typography>{keg.data.description}</Typography>}
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card variant="outlined">
                <CardHeader title="Keg" />
                <CardContent>
                  <Stack spacing={1}>
                    <KegProgress keg={keg.data} />
                    <Typography variant="body2" color="text.secondary">
                      {volume(keg.data.served_volume_ml)} served
                      {keg.data.spilled_ml > 0 ? ` · ${volume(keg.data.spilled_ml)} spilled` : ""}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            {stats.data?.volume_by_drinker &&
              Object.keys(stats.data.volume_by_drinker).length > 0 && (
                <Grid size={{ xs: 12, md: 6 }}>
                  <Card variant="outlined">
                    <CardHeader title="Top drinkers" />
                    <CardContent>
                      <VolumeByDrinkerChart data={stats.data.volume_by_drinker} limit={5} />
                    </CardContent>
                  </Card>
                </Grid>
              )}
          </Grid>
          {stats.data?.volume_by_session && (
            <Stack spacing={1}>
              <Typography variant="h5">Sessions</Typography>
              <SessionVolumeList volumeBySession={stats.data.volume_by_session} />
            </Stack>
          )}
          <Stack spacing={1}>
            <Typography variant="h5">Drinks</Typography>
            <DrinkList drinks={drinks.items} hideKeg />
            <LoadMoreButton list={drinks} />
          </Stack>
        </Stack>
      )}
    </Page>
  );
}
