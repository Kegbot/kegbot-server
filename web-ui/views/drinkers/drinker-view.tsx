import Avatar from "@mui/material/Avatar";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import { Link, useParams } from "react-router";
import { drinksList, usersRetrieve, usersStatsRetrieve } from "@/api-client";
import { VolumeByWeekdayChart } from "@/components/charts/volume-by-weekday-chart";
import { DrinkList } from "@/components/drink-list";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { SessionVolumeList } from "@/components/session-volume-list";
import { StatStrip } from "@/components/stat-badges";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { asStats } from "@/lib/stats";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";

export function DrinkerView() {
  const params = useParams();
  const username = params.username ?? "";
  const { volume } = useFormatters();

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
  const showUsername = user.data?.display_name && user.data.display_name !== username;

  return (
    <Page
      title={displayName}
      meta={showUsername ? username : undefined}
      avatar={
        <Avatar src={user.data?.picture?.resized_url ?? undefined} sx={{ width: 56, height: 56 }}>
          {displayName.charAt(0).toUpperCase()}
        </Avatar>
      }
      width="content"
      loading={user.loading}
      error={user.error}
    >
      {user.data && (
        <Stack spacing={4}>
          {stats.data && (
            <StatStrip
              cells={[
                { value: volume(stats.data.total_volume_ml ?? 0), caption: "total poured" },
                { value: stats.data.total_pours ?? 0, caption: "pours" },
                { value: stats.data.sessions_count ?? 0, caption: "sessions" },
                {
                  value:
                    stats.data.greatest_volume_id != null ? (
                      <MuiLink
                        component={Link}
                        to={`/drinks/${stats.data.greatest_volume_id}`}
                        underline="hover"
                        color="inherit"
                      >
                        {volume(stats.data.greatest_volume_ml ?? 0)}
                      </MuiLink>
                    ) : (
                      volume(stats.data.greatest_volume_ml ?? 0)
                    ),
                  caption: "biggest pour",
                },
              ]}
            />
          )}
          <Grid container spacing={4}>
            {stats.data?.volume_by_day_of_week && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Section label="Volume by day of week">
                  <VolumeByWeekdayChart data={stats.data.volume_by_day_of_week} />
                </Section>
              </Grid>
            )}
            {stats.data?.volume_by_session && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Section label="Sessions">
                  <SessionVolumeList volumeBySession={stats.data.volume_by_session} />
                </Section>
              </Grid>
            )}
          </Grid>
          <Section label="Drinks">
            <Stack spacing={1}>
              <DrinkList drinks={drinks.items} hideUser />
              <LoadMoreButton list={drinks} />
            </Stack>
          </Section>
        </Stack>
      )}
    </Page>
  );
}
