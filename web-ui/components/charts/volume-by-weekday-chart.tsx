import { BarChart } from "@mui/x-charts/BarChart";
import { useFormatters } from "@/components/use-formatters";

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
const LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/** Bar chart of poured volume by day of week. */
export function VolumeByWeekdayChart({ data }: { data: Record<string, number> }) {
  const { volume } = useFormatters();
  const values = DAYS.map((day) => data[day] ?? 0);
  return (
    <BarChart
      xAxis={[{ data: LABELS, scaleType: "band" }]}
      series={[{ data: values, valueFormatter: (v) => (v == null ? "" : volume(v)) }]}
      height={260}
    />
  );
}
