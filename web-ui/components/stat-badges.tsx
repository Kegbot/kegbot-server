import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import { useFormatters } from "@/components/use-formatters";
import type { StatsBlob } from "@/lib/stats";
import { MONO_FONT } from "@/theme/typography";

function Badge({ value, caption }: { value: ReactNode; caption: string }) {
  return (
    <Grid size={{ xs: 6, sm: 3 }}>
      <Card variant="outlined" sx={{ height: "100%" }}>
        <CardContent sx={{ py: 1.75, "&:last-child": { pb: 1.75 } }}>
          <Typography
            sx={{ fontFamily: MONO_FONT, fontWeight: 600, fontSize: "1.5rem", lineHeight: 1.3 }}
          >
            {value}
          </Typography>
          <Typography variant="overline" color="text.secondary">
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
