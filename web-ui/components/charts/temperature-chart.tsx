import { LineChart } from "@mui/x-charts/LineChart";
import type { Thermolog } from "@/api-client";
import { useChartColors } from "@/components/charts/chart-colors";
import { useConfig } from "@/components/config-context";
import { useFormatters } from "@/components/use-formatters";

/** Line chart of recent temperature readings (oldest to newest). */
export function TemperatureChart({ logs }: { logs: Thermolog[] }) {
  const { temperature } = useFormatters();
  const { me } = useConfig();
  const colors = useChartColors();
  const ordered = [...logs].reverse();
  const useFahrenheit = me.site.temperature_display_units === "f";
  return (
    <LineChart
      xAxis={[
        {
          data: ordered.map((log) => new Date(log.time)),
          scaleType: "time",
          disableLine: true,
          disableTicks: true,
        },
      ]}
      yAxis={[{ disableLine: true, disableTicks: true, width: 40 }]}
      series={[
        {
          data: ordered.map((log) => (useFahrenheit ? (log.temp * 9) / 5 + 32 : log.temp)),
          showMark: false,
          // The cool series color: temperature reads as the teal line.
          color: colors[1],
          valueFormatter: (value, context) => {
            const original = ordered[context.dataIndex];
            return original ? temperature(original.temp) : String(value);
          },
        },
      ]}
      grid={{ horizontal: true }}
      height={240}
      margin={{ top: 8, right: 8 }}
    />
  );
}
