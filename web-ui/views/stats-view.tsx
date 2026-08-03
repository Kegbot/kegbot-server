import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import { statsSystemRetrieve } from "@/api-client";
import { VolumeByDrinkerChart } from "@/components/charts/volume-by-drinker-chart";
import { VolumeByWeekdayChart } from "@/components/charts/volume-by-weekday-chart";
import { Page } from "@/components/page";
import { StatBadges } from "@/components/stat-badges";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { asStats } from "@/lib/stats";
import { useAsyncData } from "@/lib/use-async-data";

export function StatsView() {
  const { volume } = useFormatters();
  const result = useAsyncData(async () => asStats(await unwrap(statsSystemRetrieve())));
  const stats = result.data;

  return (
    <Page title="Statistics" loading={result.loading} error={result.error}>
      {stats && (
        <Stack spacing={3}>
          <StatBadges stats={stats} />
          <Grid container spacing={3}>
            {stats.volume_by_drinker && Object.keys(stats.volume_by_drinker).length > 0 && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Card variant="outlined">
                  <CardHeader title="Top drinkers" />
                  <CardContent>
                    <VolumeByDrinkerChart data={stats.volume_by_drinker} />
                  </CardContent>
                </Card>
              </Grid>
            )}
            {stats.volume_by_day_of_week && (
              <Grid size={{ xs: 12, md: 6 }}>
                <Card variant="outlined">
                  <CardHeader title="Volume by day of week" />
                  <CardContent>
                    <VolumeByWeekdayChart data={stats.volume_by_day_of_week} />
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
          {stats.largest_session?.session_id != null && (
            <Typography>
              Largest session:{" "}
              <MuiLink
                component={Link}
                to={`/sessions/id/${stats.largest_session.session_id}`}
                underline="hover"
              >
                Session #{stats.largest_session.session_id}
              </MuiLink>{" "}
              ({volume(stats.largest_session.volume_ml ?? 0)})
            </Typography>
          )}
        </Stack>
      )}
    </Page>
  );
}
