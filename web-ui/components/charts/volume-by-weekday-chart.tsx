import { BarChart } from "@mui/x-charts/BarChart";
import { useChartColors } from "@/components/charts/chart-colors";
import { useFormatters } from "@/components/use-formatters";

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
const LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/** Bar chart of poured volume by day of week. */
export function VolumeByWeekdayChart({ data }: { data: Record<string, number> }) {
  const { volume } = useFormatters();
  const colors = useChartColors();
  const values = DAYS.map((day) => data[day] ?? 0);
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
