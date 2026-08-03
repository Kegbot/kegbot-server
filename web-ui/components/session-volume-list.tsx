import MuiLink from "@mui/material/Link";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import { useFormatters } from "@/components/use-formatters";

/**
 * Session list derived from a stats blob's volume_by_session map
 * (newest session id first).
 */
export function SessionVolumeList({
  volumeBySession,
}: {
  volumeBySession: Record<string, number>;
}) {
  const { volume } = useFormatters();
  const entries = Object.entries(volumeBySession).sort(([a], [b]) => Number(b) - Number(a));
  if (entries.length === 0) {
    return <Typography color="text.secondary">No sessions yet.</Typography>;
  }
  return (
    <TableContainer sx={{ overflowX: "auto" }}>
      <Table size="small">
        <TableBody>
          {entries.map(([sessionId, sessionVolume]) => (
            <TableRow key={sessionId} hover>
              <TableCell>
                <MuiLink component={Link} to={`/sessions/id/${sessionId}`} underline="hover">
                  Session #{sessionId}
                </MuiLink>
              </TableCell>
              <TableCell align="right">{volume(sessionVolume)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
