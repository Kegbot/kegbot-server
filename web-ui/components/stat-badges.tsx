import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import { useFormatters } from "@/components/use-formatters";
import type { StatsBlob } from "@/lib/stats";

function Badge({ value, caption }: { value: ReactNode; caption: string }) {
  return (
    <Grid size={{ xs: 6, sm: 3 }}>
      <Card variant="outlined" sx={{ textAlign: "center", height: "100%" }}>
        <CardContent>
          <Typography variant="h5">{value}</Typography>
          <Typography variant="caption" color="text.secondary">
            {caption}
          </Typography>
        </CardContent>
      </Card>
    </Grid>
  );
}

/** Row of headline stats derived from a stats blob. */
export function StatBadges({ stats }: { stats: StatsBlob }) {
  const { volume } = useFormatters();
  return (
    <Grid container spacing={2}>
      <Badge value={volume(stats.total_volume_ml ?? 0)} caption="total poured" />
      <Badge value={stats.total_pours ?? 0} caption="pours" />
      <Badge value={stats.registered_drinkers?.length ?? 0} caption="drinkers" />
      <Badge value={stats.sessions_count ?? 0} caption="sessions" />
    </Grid>
  );
}
