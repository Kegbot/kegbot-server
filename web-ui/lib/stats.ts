/**
 * Shape of the stats blob computed by pykeg/core/stats.py.
 *
 * The server serializes it as an untyped JSON object; this hand-written
 * type mirrors the StatsBuilder methods. Keep the two in sync.
 */
export interface StatsBlob {
  last_drink_id?: number;
  keg_ids?: number[];
  total_volume_ml?: number;
  total_pours?: number;
  average_volume_ml?: number;
  greatest_volume_ml?: number;
  greatest_volume_id?: number;
  /** Keys are day names ("monday" .. "sunday"). */
  volume_by_day_of_week?: Record<string, number>;
  /** Usernames (ids are translated server-side). */
  registered_drinkers?: string[];
  sessions_count?: number;
  /** Keys are years ("2026"). */
  volume_by_year?: Record<string, number>;
  has_guest_pour?: boolean;
  /** Keys are usernames. */
  volume_by_drinker?: Record<string, number>;
  /** Keys are session ids. */
  volume_by_session?: Record<string, number>;
  largest_session?: {
    session_id?: number;
    volume_ml?: number;
  };
}

export function asStats(value: unknown): StatsBlob {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as StatsBlob;
  }
  return {};
}
