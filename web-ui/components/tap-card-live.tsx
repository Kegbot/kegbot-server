import type { KegTap } from "@/api-client";
import { thermoLogsList } from "@/api-client";
import { TapCard } from "@/components/tap-card";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

/** TapCard that also fetches the latest temperature for the tap's sensor. */
export function TapCardLive({ tap }: { tap: KegTap }) {
  const { temperature } = useFormatters();
  const sensorId = tap.temperature_sensor_id;
  const reading = useAsyncData(
    async () => {
      const page = await unwrap(thermoLogsList({ query: { sensor: sensorId, page_size: 1 } }));
      return page.results?.[0] ?? null;
    },
    { deps: [sensorId], enabled: sensorId != null, pollMs: 60_000 },
  );

  const tempC = reading.data?.temp ?? null;
  return (
    <TapCard
      tap={tap}
      temperatureC={tempC}
      temperatureLabel={tempC != null ? temperature(tempC) : undefined}
    />
  );
}
