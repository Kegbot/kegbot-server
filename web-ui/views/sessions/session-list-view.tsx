import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { Link, useParams } from "react-router";
import type { DrinkingSession } from "@/api-client";
import { sessionsList } from "@/api-client";
import { EmptyState } from "@/components/empty-state";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { useCursorList } from "@/lib/use-cursor-list";
import { MONO_FONT } from "@/theme/typography";

export function sessionTitle(session: DrinkingSession): string {
  return session.name || `Session #${session.id}`;
}

/**
 * Session archive. Optional :year/:month/:day route params narrow the
 * range, mirroring the old date-hierarchy URLs.
 */
export function SessionListView() {
  const params = useParams();
  const { volume } = useFormatters();
  const year = params.year ? Number(params.year) : undefined;
  const month = params.month ? Number(params.month) : undefined;
  const day = params.day ? Number(params.day) : undefined;

  const list = useCursorList(
    (cursor) => unwrap(sessionsList({ query: { cursor, year, month, day } })),
    [year, month, day],
  );

  const suffix = [year, month, day].filter((v) => v !== undefined).join("-");
  const title = suffix ? `Sessions · ${suffix}` : "Sessions";

  return (
    <Page title={title} loading={list.loading} error={list.error}>
      <Stack spacing={2}>
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
                {list.items.map((session) => (
                  <TableRow key={session.id} hover>
                    <TableCell>
                      <MuiLink component={Link} to={`/sessions/id/${session.id}`} underline="hover">
                        {sessionTitle(session)}
                      </MuiLink>
                    </TableCell>
                    <TableCell sx={{ color: "text.secondary", whiteSpace: "nowrap" }}>
                      {formatDateTime(session.start_time)}
                    </TableCell>
                    <TableCell align="right" sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap" }}>
                      {volume(session.volume_ml ?? 0)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
        <LoadMoreButton list={list} />
      </Stack>
    </Page>
  );
}
