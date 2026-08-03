import { BarChart } from "@mui/x-charts/BarChart";
import { useChartColors } from "@/components/charts/chart-colors";
import { useFormatters } from "@/components/use-formatters";

export interface VolumeByDrinkerChartProps {
  data: Record<string, number>;
  /** Show at most this many drinkers (largest first). */
  limit?: number;
}

/** Horizontal bar chart of poured volume by drinker. */
export function VolumeByDrinkerChart({ data, limit = 10 }: VolumeByDrinkerChartProps) {
  const { volume } = useFormatters();
  const colors = useChartColors();
  const entries = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit);
  return (
    <BarChart
      layout="horizontal"
      yAxis={[
        {
          data: entries.map(([name]) => name),
          scaleType: "band",
          width: 120,
          disableLine: true,
          disableTicks: true,
        },
      ]}
      xAxis={[{ disableLine: true, disableTicks: true }]}
      series={[
        {
          data: entries.map(([, value]) => value),
          valueFormatter: (v) => (v == null ? "" : volume(v)),
        },
      ]}
      colors={colors}
      borderRadius={4}
      grid={{ vertical: true }}
      height={Math.max(160, entries.length * 40)}
      margin={{ top: 8, right: 8 }}
    />
  );
}
