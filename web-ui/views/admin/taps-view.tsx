import AddIcon from "@mui/icons-material/Add";
import Button from "@mui/material/Button";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import { type FormEvent, useState } from "react";
import { Link } from "react-router";
import { tapsCreate, tapsList } from "@/api-client";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

export function TapsView() {
  const { showMessage } = useSnackbar();
  const taps = useAsyncData(
    async () => (await unwrap(tapsList({ query: { page_size: 100 } }))).results ?? [],
  );
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    try {
      await unwrap(tapsCreate({ body: { name } }));
      showMessage(`Tap "${name}" created.`);
      setName("");
      taps.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="Taps" loading={taps.loading} error={taps.error}>
      <Stack spacing={3}>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Tap</TableCell>
                <TableCell>Current keg</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(taps.data ?? []).map((tap) => (
                <TableRow key={tap.id} hover>
                  <TableCell>
                    <MuiLink component={Link} to={`/kegadmin/taps/${tap.id}`} underline="hover">
                      {tap.name}
                    </MuiLink>
                  </TableCell>
                  <TableCell>
                    {tap.current_keg ? tap.current_keg.beverage.name : "— empty —"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <form onSubmit={onCreate}>
          <Stack direction="row" spacing={2} sx={{ alignItems: "center", maxWidth: 480 }}>
            <TextField
              label="New tap name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              size="small"
              required
              sx={{ flexGrow: 1 }}
            />
            <Button type="submit" startIcon={<AddIcon />} variant="outlined" disabled={busy}>
              Add tap
            </Button>
          </Stack>
        </form>
      </Stack>
    </Page>
  );
}
