import Box from "@mui/material/Box";
import MuiLink from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { DateParts } from "@/lib/format";
import { monthName } from "@/lib/format";
import { MONO_FONT } from "@/theme/typography";

const WEEKDAYS = ["S", "M", "T", "W", "T", "F", "S"];

export interface MonthCalendarProps {
  year: number;
  /** 1-12. */
  month: number;
  /** Days of this month that have sessions (clickable, highlighted). */
  activeDays: number[];
  /** Smaller cells for the year-overview grid. */
  compact?: boolean;
  /** Link the month name to the month's archive page. */
  linkMonth?: boolean;
  /** Today's date (in the site timezone) for the today marker. */
  today?: DateParts;
}

/**
 * Mini calendar for the session archive: weekday-aligned day grid
 * (weeks start Sunday) with session days highlighted and linked.
 */
export function MonthCalendar({
  year,
  month,
  activeDays,
  compact,
  linkMonth,
  today,
}: MonthCalendarProps) {
  const dayCount = new Date(year, month, 0).getDate();
  const firstWeekday = new Date(year, month - 1, 1).getDay();
  const active = new Set(activeDays);
  // Compact calendars have fixed small cells; full-size ones fill their
  // container with square cells.
  const cellSize = compact ? { height: 26 } : { aspectRatio: "1 / 1", minHeight: 40 };
  const fontSize = compact ? "0.6875rem" : "0.875rem";

  const title = linkMonth ? (
    <MuiLink
      component={Link}
      to={`/sessions/${year}/${month}`}
      underline="hover"
      color={active.size > 0 ? "text.primary" : "text.secondary"}
    >
      {monthName(month)}
    </MuiLink>
  ) : (
    monthName(month)
  );

  return (
    <Box sx={{ width: "100%", maxWidth: compact ? 26 * 7 + 6 * 2 : undefined }}>
      <Typography variant="subtitle2" component="div" sx={{ mb: 0.5 }}>
        {title}
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: "2px",
          justifyItems: "stretch",
        }}
      >
        {WEEKDAYS.map((label, index) => (
          <Typography
            // biome-ignore lint/suspicious/noArrayIndexKey: static weekday header
            key={`${label}-${index}`}
            variant="caption"
            sx={{
              fontFamily: MONO_FONT,
              fontSize: compact ? "0.5625rem" : "0.6875rem",
              color: "text.secondary",
              opacity: 0.7,
              textAlign: "center",
              lineHeight: `${compact ? 16 : 22}px`,
            }}
          >
            {label}
          </Typography>
        ))}
        {Array.from({ length: firstWeekday }, (_, index) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: leading blanks
          <Box key={`blank-${index}`} />
        ))}
        {Array.from({ length: dayCount }, (_, index) => {
          const day = index + 1;
          const isToday = today?.year === year && today.month === month && today.day === day;
          const common = {
            ...cellSize,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: 1,
            fontFamily: MONO_FONT,
            fontSize,
            boxShadow: isToday ? "inset 0 0 0 1px currentColor" : "none",
          } as const;
          if (active.has(day)) {
            return (
              <Box
                key={day}
                component={Link}
                to={`/sessions/${year}/${month}/${day}`}
                sx={{
                  ...common,
                  bgcolor: "primary.main",
                  color: "primary.contrastText",
                  fontWeight: 600,
                  textDecoration: "none",
                  "&:hover": { bgcolor: "primary.dark" },
                }}
              >
                {day}
              </Box>
            );
          }
          return (
            <Box key={day} sx={{ ...common, color: "text.secondary", opacity: 0.55 }}>
              {day}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
