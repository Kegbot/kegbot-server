import Avatar from "@mui/material/Avatar";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useParams } from "react-router";
import { drinksList, usersRetrieve, usersStatsRetrieve } from "@/api";
import { VolumeByWeekdayChart } from "@/components/charts/volume-by-weekday-chart";
import { DrinkList } from "@/components/drink-list";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { SessionVolumeList } from "@/components/session-volume-list";
import { StatBadges } from "@/components/stat-badges";
import { unwrap } from "@/lib/api";
import { asStats } from "@/lib/stats";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";

export function DrinkerView() {
  const params = useParams();
  const username = params.username ?? "";

  const user = useAsyncData(() => unwrap(usersRetrieve({ path: { username } })), {
    deps: [username],
  });
  const stats = useAsyncData(
    async () => asStats(await unwrap(usersStatsRetrieve({ path: { username } }))),
    { deps: [username] },
  );
  const drinks = useCursorList(
    (cursor) => unwrap(drinksList({ query: { username, cursor } })),
    [username],
  );

  const displayName = user.data?.display_name || username;

  return (
    <Page title={displayName} hideHeading loading={user.loading} error={user.error}>
      {user.data && (
        <Stack spacing={3}>
          <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
            <Avatar
              src={user.data.picture?.resized_url ?? undefined}
              sx={{ width: 64, height: 64 }}
            >
              {displayName.charAt(0).toUpperCase()}
            </Avatar>
            <Stack>
              <Typography variant="h4">{displayName}</Typography>
              {user.data.display_name && user.data.display_name !== username && (
                <Typography color="text.secondary">{username}</Typography>
              )}
            </Stack>
          </Stack>
          {stats.data && <StatBadges stats={stats.data} />}
          <Grid container spacing={3}>
            {stats.data?.volume_by_day_of_week && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Card variant="outlined">
                  <CardHeader title="Volume by day of week" />
                  <CardContent>
                    <VolumeByWeekdayChart data={stats.data.volume_by_day_of_week} />
                  </CardContent>
                </Card>
              </Grid>
            )}
            {stats.data?.volume_by_session && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Card variant="outlined">
                  <CardHeader title="Sessions" />
                  <CardContent>
                    <SessionVolumeList volumeBySession={stats.data.volume_by_session} />
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
          <Stack spacing={1}>
            <Typography variant="h5">Drinks</Typography>
            <DrinkList drinks={drinks.items} hideUser />
            <LoadMoreButton list={drinks} />
          </Stack>
        </Stack>
      )}
    </Page>
  );
}
