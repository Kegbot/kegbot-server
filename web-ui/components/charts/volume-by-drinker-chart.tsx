import { BarChart } from "@mui/x-charts/BarChart";
import { useFormatters } from "@/components/use-formatters";

export interface VolumeByDrinkerChartProps {
  data: Record<string, number>;
  /** Show at most this many drinkers (largest first). */
  limit?: number;
}

/** Horizontal bar chart of poured volume by drinker. */
export function VolumeByDrinkerChart({ data, limit = 10 }: VolumeByDrinkerChartProps) {
  const { volume } = useFormatters();
  const entries = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit);
  return (
    <BarChart
      layout="horizontal"
      yAxis={[{ data: entries.map(([name]) => name), scaleType: "band", width: 110 }]}
      series={[
        {
          data: entries.map(([, value]) => value),
          valueFormatter: (v) => (v == null ? "" : volume(v)),
        },
      ]}
      height={Math.max(180, entries.length * 44)}
    />
  );
}
