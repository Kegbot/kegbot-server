/** Route-param helpers: react-router params are untyped strings. */

/**
 * Parses a positive-integer route param. Returns undefined for missing
 * or malformed values ("null", "NaN", "12abc") so garbage never reaches
 * an API query.
 */
export function intParam(value: string | undefined): number | undefined {
  if (value === undefined || !/^\d+$/.test(value)) {
    return undefined;
  }
  return Number(value);
}
