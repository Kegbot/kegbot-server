import { LineChart } from "@mui/x-charts/LineChart";
import type { Thermolog } from "@/api-client";
import { useConfig } from "@/components/config-context";
import { useFormatters } from "@/components/use-formatters";

/** Line chart of recent temperature readings (oldest to newest). */
export function TemperatureChart({ logs }: { logs: Thermolog[] }) {
  const { temperature } = useFormatters();
  const { me } = useConfig();
  const ordered = [...logs].reverse();
  const useFahrenheit = me.site.temperature_display_units === "f";
  return (
    <LineChart
      xAxis={[
        {
          data: ordered.map((log) => new Date(log.time)),
          scaleType: "time",
        },
      ]}
      series={[
        {
          data: ordered.map((log) => (useFahrenheit ? (log.temp * 9) / 5 + 32 : log.temp)),
          showMark: false,
          valueFormatter: (value, context) => {
            const original = ordered[context.dataIndex];
            return original ? temperature(original.temp) : String(value);
          },
        },
      ]}
      height={260}
    />
  );
}
