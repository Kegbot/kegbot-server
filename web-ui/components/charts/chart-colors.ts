import { useColorScheme } from "@mui/material/styles";
import { CHART_SERIES_DARK, CHART_SERIES_LIGHT } from "@/theme/palette";

/** Validated chart series colors for the active color scheme. */
export function useChartColors(): string[] {
  const { mode, systemMode } = useColorScheme();
  const resolved = (mode === "system" ? systemMode : mode) ?? "light";
  return resolved === "dark" ? CHART_SERIES_DARK : CHART_SERIES_LIGHT;
}
