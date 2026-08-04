import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router";
import type { DrinkingSession, SessionDirectory } from "@/api-client";
import { sessionsDirectoryRetrieve, sessionsList } from "@/api-client";
import type { Crumb } from "@/components/breadcrumbs";
import { useConfig } from "@/components/config-context";
import { EmptyState } from "@/components/empty-state";
import { LoadMoreButton } from "@/components/load-more-button";
import { MonthCalendar } from "@/components/month-calendar";
import { Page } from "@/components/page";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { datePartsInZone, formatDateTime, monthName } from "@/lib/format";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";
import { MONO_FONT } from "@/theme/typography";

export function sessionTitle(session: DrinkingSession): string {
  return session.name || `Session #${session.id}`;
}

/** Date-hierarchy breadcrumb trail for a (year, month, day) position. */
export function sessionArchiveCrumbs(
  year?: number,
  month?: number,
  day?: number,
  current?: string,
): Crumb[] {
  const crumbs: Crumb[] = [{ label: "Sessions", to: "/sessions" }];
  if (year !== undefined) {
    crumbs.push({ label: String(year), to: `/sessions/${year}` });
  }
  if (year !== undefined && month !== undefined) {
    crumbs.push({ label: monthName(month), to: `/sessions/${year}/${month}` });
  }
  if (year !== undefined && month !== undefined && day !== undefined) {
    crumbs.push({ label: String(day), to: `/sessions/${year}/${month}/${day}` });
  }
  if (current) {
    crumbs.push({ label: current });
  } else {
    // The last position is the current page; drop its link.
    const last = crumbs[crumbs.length - 1];
    if (last) {
      last.to = undefined;
    }
  }
  return crumbs;
}

/** Session days for (year, month) from the archive directory. */
function activeDays(directory: SessionDirectory | null, year: number, month: number): number[] {
  const yearEntry = directory?.years.find((entry) => entry.year === year);
  return yearEntry?.months.find((entry) => entry.month === month)?.days ?? [];
}

/**
 * Session archive. Optional :year/:month/:day route params narrow the
 * range, mirroring the old date-hierarchy URLs. Breadcrumbs, year
 * chips, and weekday-aligned calendars expose the hierarchy.
 */
export function SessionListView() {
  const params = useParams();
  const { volume } = useFormatters();
  const { me } = useConfig();
  const directory = useAsyncData(() => unwrap(sessionsDirectoryRetrieve()));
  const year = params.year ? Number(params.year) : undefined;
  const month = params.month ? Number(params.month) : undefined;
  const day = params.day ? Number(params.day) : undefined;

  const list = useCursorList(
    (cursor) => unwrap(sessionsList({ query: { cursor, year, month, day } })),
    [year, month, day],
  );

  const title =
    year === undefined
      ? "Sessions"
      : month === undefined
        ? `Sessions in ${year}`
        : day === undefined
          ? `${monthName(month)} ${year}`
          : `${monthName(month)} ${day}, ${year}`;

  const today = datePartsInZone(new Date().toISOString(), me.site.timezone);
  const years = directory.data?.years ?? [];

  return (
    <Page
      title={title}
      breadcrumbs={sessionArchiveCrumbs(year, month, day)}
      loading={list.loading}
      error={list.error}
    >
      <Stack spacing={3}>
        {/* Root: years with sessions, as chunky tiles. */}
        {year === undefined && years.length > 0 && (
          <Grid container spacing={2}>
            {years.map((entry) => (
              <Grid key={entry.year} size={{ xs: 6, sm: 4, md: 3 }}>
                <Paper
                  variant="outlined"
                  component={Link}
                  to={`/sessions/${entry.year}`}
                  sx={{
                    display: "block",
                    px: 2.5,
                    py: 2,
                    textDecoration: "none",
                    color: "inherit",
                    transition: "border-color 120ms ease",
                    "&:hover": { borderColor: "primary.main" },
                  }}
                >
                  <Typography
                    sx={{
                      fontFamily: MONO_FONT,
                      fontWeight: 600,
                      fontSize: "1.75rem",
                      lineHeight: 1.2,
                    }}
                  >
                    {entry.year}
                  </Typography>
                  <Typography variant="overline" color="text.secondary" component="div">
                    {entry.count === 1 ? "1 session" : `${entry.count} sessions`}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
        {/* Year: every month as a mini calendar. */}
        {year !== undefined && month === undefined && directory.data && (
          <Grid container spacing={3}>
            {Array.from({ length: 12 }, (_, index) => index + 1).map((m) => (
              <Grid key={m} size={{ xs: 6, sm: 4, md: 3 }}>
                <MonthCalendar
                  year={year}
                  month={m}
                  activeDays={activeDays(directory.data, year, m)}
                  compact
                  linkMonth
                  today={today}
                />
              </Grid>
            ))}
          </Grid>
        )}
        {/* Month: one full calendar. */}
        {year !== undefined && month !== undefined && day === undefined && directory.data && (
          <MonthCalendar
            year={year}
            month={month}
            activeDays={activeDays(directory.data, year, month)}
            today={today}
          />
        )}
        {list.items.length === 0 && !list.loading && (
          <EmptyState title="No sessions found." hint="Try a wider date range." />
        )}
        {list.items.length > 0 && (
          <TableContainer sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Session</TableCell>
                  <TableCell>Started</TableCell>
                  <TableCell align="right">Volume</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {list.items.map((session) => {
                  const started = datePartsInZone(session.start_time, me.site.timezone);
                  const dayPath = `/sessions/${started.year}/${started.month}/${started.day}`;
                  return (
                    <TableRow key={session.id} hover>
                      <TableCell>
                        <MuiLink
                          component={Link}
                          to={`/sessions/id/${session.id}`}
                          underline="hover"
                        >
                          {sessionTitle(session)}
                        </MuiLink>
                      </TableCell>
                      <TableCell sx={{ whiteSpace: "nowrap" }}>
                        <MuiLink
                          component={Link}
                          to={dayPath}
                          underline="hover"
                          color="inherit"
                          sx={{ color: "text.secondary" }}
                          title="Browse this day"
                        >
                          {formatDateTime(session.start_time)}
                        </MuiLink>
                      </TableCell>
                      <TableCell align="right" sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap" }}>
                        {volume(session.volume_ml ?? 0)}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <LoadMoreButton list={list} />
      </Stack>
    </Page>
  );
}
