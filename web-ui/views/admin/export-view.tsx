import Button from "@mui/material/Button";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { adminBackupsCreate, adminBackupsDestroy, adminBackupsRetrieve } from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

interface BackupEntry {
  backup_name: string;
  url: string;
  size_bytes: number;
  created_time?: string;
  server_version?: string;
}

function formatSize(bytes: number): string {
  if (bytes > 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
  return `${Math.round(bytes / 1024)} KB`;
}

export function ExportView() {
  const confirm = useConfirm();
  const { showMessage } = useSnackbar();
  const backups = useAsyncData(
    async () => (await unwrap(adminBackupsRetrieve())) as unknown as BackupEntry[],
    { pollMs: 15_000 },
  );
  const [busy, setBusy] = useState(false);

  const build = async () => {
    setBusy(true);
    try {
      await unwrap(adminBackupsCreate());
      showMessage("Backup started; it will appear below when finished.");
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  const remove = async (name: string) => {
    if (
      !(await confirm({
        title: `Delete backup ${name}?`,
        confirmText: "Delete",
        destructive: true,
      }))
    ) {
      return;
    }
    try {
      await unwrap(adminBackupsDestroy({ path: { filename: name } }));
      showMessage("Backup deleted.");
      backups.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page
      title="Backup / Export"
      loading={backups.loading}
      error={backups.error}
      headerRight={
        <Button variant="contained" onClick={() => void build()} disabled={busy}>
          Build new backup
        </Button>
      }
    >
      {backups.data && backups.data.length === 0 ? (
        <Typography color="text.secondary">No backups yet.</Typography>
      ) : (
        <Stack spacing={2}>
          <TableContainer sx={{ overflowX: "auto" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Backup</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Size</TableCell>
                  <TableCell />
                </TableRow>
              </TableHead>
              <TableBody>
                {(backups.data ?? []).map((backup) => (
                  <TableRow key={backup.backup_name} hover>
                    <TableCell>
                      <MuiLink href={backup.url} underline="hover">
                        {backup.backup_name}
                      </MuiLink>
                    </TableCell>
                    <TableCell>{backup.created_time ?? "—"}</TableCell>
                    <TableCell align="right">{formatSize(backup.size_bytes)}</TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        color="error"
                        onClick={() => void remove(backup.backup_name)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Stack>
      )}
    </Page>
  );
}
