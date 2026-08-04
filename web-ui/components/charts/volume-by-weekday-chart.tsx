import { BarChart } from "@mui/x-charts/BarChart";
import { useChartColors } from "@/components/charts/chart-colors";
import { useFormatters } from "@/components/use-formatters";

// Blob keys are strftime("%w"): "0" (Sunday) through "6" (Saturday).
// Sunday-first display matches the archive calendars.
const DAY_KEYS = ["0", "1", "2", "3", "4", "5", "6"];
const LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** Bar chart of poured volume by day of week. */
export function VolumeByWeekdayChart({ data }: { data: Record<string, number> }) {
  const { volume } = useFormatters();
  const colors = useChartColors();
  const values = DAY_KEYS.map((key) => data[key] ?? 0);
  return (
    <BarChart
      xAxis={[{ data: LABELS, scaleType: "band", disableLine: true, disableTicks: true }]}
      yAxis={[{ disableLine: true, disableTicks: true, width: 40 }]}
      series={[{ data: values, valueFormatter: (v) => (v == null ? "" : volume(v)) }]}
      colors={colors}
      borderRadius={4}
      grid={{ horizontal: true }}
      height={240}
      margin={{ top: 8, right: 8 }}
    />
  );
}
