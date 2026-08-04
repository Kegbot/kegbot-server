import Chip from "@mui/material/Chip";
import MuiLink from "@mui/material/Link";
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
import { Page } from "@/components/page";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { datePartsInZone, formatDateTime } from "@/lib/format";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";
import { MONO_FONT } from "@/theme/typography";

export function sessionTitle(session: DrinkingSession): string {
  return session.name || `Session #${session.id}`;
}

export function monthName(month: number, style: "long" | "short" = "long"): string {
  return new Date(2000, month - 1, 1).toLocaleString(undefined, { month: style });
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

interface DrillTarget {
  label: string;
  to: string;
}

/** Next-level drilldown targets from the server's archive directory. */
function drillTargets(
  directory: SessionDirectory | null,
  year?: number,
  month?: number,
  day?: number,
): DrillTarget[] {
  if (!directory || day !== undefined) {
    return [];
  }
  if (year === undefined) {
    return directory.years.map((entry) => ({
      label: String(entry.year),
      to: `/sessions/${entry.year}`,
    }));
  }
  const yearEntry = directory.years.find((entry) => entry.year === year);
  if (!yearEntry) {
    return [];
  }
  if (month === undefined) {
    return yearEntry.months.map((entry) => ({
      label: monthName(entry.month, "short"),
      to: `/sessions/${year}/${entry.month}`,
    }));
  }
  const monthEntry = yearEntry.months.find((entry) => entry.month === month);
  if (!monthEntry) {
    return [];
  }
  return monthEntry.days.map((d) => ({
    label: `${monthName(month, "short")} ${d}`,
    to: `/sessions/${year}/${month}/${d}`,
  }));
}

/**
 * Session archive. Optional :year/:month/:day route params narrow the
 * range, mirroring the old date-hierarchy URLs; breadcrumbs and drill
 * chips expose the hierarchy.
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

  const drills = drillTargets(directory.data, year, month, day);
  const drillLabel =
    year === undefined ? "Browse by year" : month === undefined ? "Months" : "Days";

  return (
    <Page
      title={title}
      breadcrumbs={sessionArchiveCrumbs(year, month, day)}
      loading={list.loading}
      error={list.error}
    >
      <Stack spacing={2.5}>
        {drills.length > 0 && (
          <Stack direction="row" spacing={1} sx={{ alignItems: "center", flexWrap: "wrap" }}>
            <Typography variant="overline" color="text.secondary">
              {drillLabel}
            </Typography>
            {drills.map((drill) => (
              <Chip
                key={drill.to}
                label={drill.label}
                component={Link}
                to={drill.to}
                clickable
                size="small"
                variant="outlined"
              />
            ))}
          </Stack>
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
