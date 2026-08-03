import { useMemo } from "react";
import { useConfig } from "@/components/config-context";
import {
  formatRelativeTime,
  formatTemperature,
  formatVolume,
  type TemperatureUnits,
  type VolumeUnits,
} from "@/lib/format";

export interface Formatters {
  volume: (volumeMl: number) => string;
  temperature: (tempC: number) => string;
  relative: (iso: string) => string;
}

/** Unit-aware formatters bound to the site's display settings. */
export function useFormatters(): Formatters {
  const { me } = useConfig();
  const volumeUnits = me.site.volume_display_units as VolumeUnits;
  const temperatureUnits = me.site.temperature_display_units as TemperatureUnits;
  return useMemo(
    () => ({
      volume: (volumeMl) => formatVolume(volumeMl, volumeUnits),
      temperature: (tempC) => formatTemperature(tempC, temperatureUnits),
      relative: (iso) => formatRelativeTime(iso),
    }),
    [volumeUnits, temperatureUnits],
  );
}
