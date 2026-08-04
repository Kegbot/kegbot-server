/** Display formatting helpers, honoring the site's unit settings. */

const ML_PER_OUNCE = 29.5735295625;
const ML_PER_PINT = ML_PER_OUNCE * 16;

export type VolumeUnits = "metric" | "imperial";
export type TemperatureUnits = "f" | "c";

export function formatVolume(volumeMl: number, units: VolumeUnits): string {
  if (units === "metric") {
    if (volumeMl < 500) {
      return `${Math.round(volumeMl)} mL`;
    }
    return `${(volumeMl / 1000).toFixed(1)} L`;
  }
  const ounces = volumeMl / ML_PER_OUNCE;
  if (ounces < 32) {
    return `${ounces.toFixed(1)} oz`;
  }
  return `${(volumeMl / ML_PER_PINT).toFixed(1)} pints`;
}

export function formatTemperature(tempC: number, units: TemperatureUnits): string {
  if (units === "f") {
    return `${((tempC * 9) / 5 + 32).toFixed(1)}° F`;
  }
  return `${tempC.toFixed(1)}° C`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { dateStyle: "medium" });
}

const RELATIVE_UNITS: Array<[Intl.RelativeTimeFormatUnit, number]> = [
  ["year", 365 * 24 * 3600],
  ["month", 30 * 24 * 3600],
  ["day", 24 * 3600],
  ["hour", 3600],
  ["minute", 60],
];

const COMPACT_UNITS: Array<[string, number]> = [
  ["y", 365 * 24 * 3600],
  ["mo", 30 * 24 * 3600],
  ["d", 24 * 3600],
  ["h", 3600],
  ["m", 60],
];

/** Compact relative time for tight gutters: "now", "4m", "2h", "3d". */
export function formatCompactRelative(iso: string, now: Date = new Date()): string {
  const seconds = Math.abs((now.getTime() - new Date(iso).getTime()) / 1000);
  for (const [suffix, unitSeconds] of COMPACT_UNITS) {
    if (seconds >= unitSeconds) {
      return `${Math.round(seconds / unitSeconds)}${suffix}`;
    }
  }
  return "now";
}

export function formatRelativeTime(iso: string, now: Date = new Date()): string {
  const seconds = (new Date(iso).getTime() - now.getTime()) / 1000;
  const magnitude = Math.abs(seconds);
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  for (const [unit, unitSeconds] of RELATIVE_UNITS) {
    if (magnitude >= unitSeconds) {
      return formatter.format(Math.round(seconds / unitSeconds), unit);
    }
  }
  return "just now";
}

export interface DateParts {
  year: number;
  month: number;
  day: number;
}

/** Localized month name for a 1-12 month number. */
export function monthName(month: number, style: "long" | "short" = "long"): string {
  return new Date(2000, month - 1, 1).toLocaleString(undefined, { month: style });
}

/**
 * Calendar date of an instant in the given IANA timezone (falls back
 * to the browser's). The session archive buckets by the *site's*
 * timezone, so archive links must be derived with it.
 */
export function datePartsInZone(iso: string, timeZone?: string | null): DateParts {
  const date = new Date(iso);
  try {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: timeZone ?? undefined,
      year: "numeric",
      month: "numeric",
      day: "numeric",
    }).formatToParts(date);
    const part = (type: string) => Number(parts.find((p) => p.type === type)?.value);
    const result = { year: part("year"), month: part("month"), day: part("day") };
    if (
      Number.isFinite(result.year) &&
      Number.isFinite(result.month) &&
      Number.isFinite(result.day)
    ) {
      return result;
    }
  } catch {
    // Unknown timezone id; fall through to browser-local.
  }
  return { year: date.getFullYear(), month: date.getMonth() + 1, day: date.getDate() };
}

/** Pour duration in seconds → "8s", "1m 12s"; em dash when unknown. */
export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds || seconds <= 0) {
    return "—";
  }
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  return rest > 0 ? `${minutes}m ${rest}s` : `${minutes}m`;
}

/** Percent (0-100) of a keg remaining, clamped. */
export function kegPercentFull(servedMl: number, spilledMl: number, fullMl: number): number {
  if (!fullMl) {
    return 0;
  }
  const remaining = fullMl - servedMl - spilledMl;
  return Math.min(100, Math.max(0, (remaining / fullMl) * 100));
}
