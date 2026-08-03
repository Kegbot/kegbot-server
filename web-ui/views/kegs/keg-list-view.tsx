import Chip from "@mui/material/Chip";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { Link } from "react-router";
import type { Keg } from "@/api-client";
import { kegsList } from "@/api-client";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useFormatters } from "@/components/use-formatters";
import { unwrap } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { useCursorList } from "@/lib/use-cursor-list";

export function kegStatusChip(keg: Keg) {
  const color =
    keg.status === "on_tap" ? "success" : keg.status === "available" ? "info" : "default";
  const label =
    keg.status === "on_tap" ? "On tap" : keg.status === "available" ? "Available" : "Finished";
  return <Chip size="small" color={color} label={label} />;
}

export function KegListView() {
  const { volume } = useFormatters();
  const list = useCursorList((cursor) => unwrap(kegsList({ query: { cursor } })));

  return (
    <Page title="Kegs" loading={list.loading} error={list.error}>
      <Stack spacing={2}>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Keg</TableCell>
                <TableCell>Beverage</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Served</TableCell>
                <TableCell>First tapped</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {list.items.map((keg) => (
                <TableRow key={keg.id} hover>
                  <TableCell>
                    <MuiLink component={Link} to={`/kegs/${keg.id}`} underline="hover">
                      Keg #{keg.id}
                    </MuiLink>
                  </TableCell>
                  <TableCell>{keg.beverage.name}</TableCell>
                  <TableCell>{kegStatusChip(keg)}</TableCell>
                  <TableCell align="right">{volume(keg.served_volume_ml)}</TableCell>
                  <TableCell>{formatDate(keg.start_time)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={list} />
      </Stack>
    </Page>
  );
}
