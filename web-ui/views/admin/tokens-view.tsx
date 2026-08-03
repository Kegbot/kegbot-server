import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import { useState } from "react";
import type { AuthenticationToken } from "@/api";
import {
  authTokensCreate,
  authTokensDestroy,
  authTokensList,
  authTokensPartialUpdate,
  usersList,
} from "@/api";
import { useConfirm } from "@/components/confirm-context";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";

interface EditorState {
  token: AuthenticationToken | null;
  authDevice: string;
  tokenValue: string;
  niceName: string;
  userId: string;
  enabled: boolean;
}

export function TokensView() {
  const { showMessage } = useSnackbar();
  const confirm = useConfirm();
  const [search, setSearch] = useState("");
  const tokens = useCursorList(
    (cursor) => unwrap(authTokensList({ query: { cursor, search: search || undefined } })),
    [search],
  );
  const users = useAsyncData(
    async () => (await unwrap(usersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    if (!editor) {
      return;
    }
    setBusy(true);
    const body = {
      auth_device: editor.authDevice,
      token_value: editor.tokenValue,
      nice_name: editor.niceName,
      user: editor.userId ? Number(editor.userId) : null,
      enabled: editor.enabled,
    };
    try {
      if (editor.token) {
        await unwrap(authTokensPartialUpdate({ path: { id: editor.token.id }, body }));
        showMessage("Token updated.");
      } else {
        await unwrap(authTokensCreate({ body }));
        showMessage("Token created.");
      }
      setEditor(null);
      tokens.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  const remove = async (token: AuthenticationToken) => {
    if (
      await confirm({
        title: "Delete this token?",
        confirmText: "Delete",
        destructive: true,
      })
    ) {
      try {
        await unwrap(authTokensDestroy({ path: { id: token.id } }));
        showMessage("Token deleted.");
        tokens.reload();
      } catch (error) {
        showMessage(toErrorMessage(error), "error");
      }
    }
  };

  const usernameFor = (userId: number | null | undefined) =>
    users.data?.find((user) => user.id === userId)?.username ??
    (userId != null ? `#${userId}` : "—");

  return (
    <Page
      title="Tokens"
      loading={tokens.loading}
      error={tokens.error}
      headerRight={
        <Button
          variant="contained"
          onClick={() =>
            setEditor({
              token: null,
              authDevice: "core.rfid",
              tokenValue: "",
              niceName: "",
              userId: "",
              enabled: true,
            })
          }
        >
          Add token
        </Button>
      }
    >
      <Stack spacing={2}>
        <TextField
          label="Search tokens"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ maxWidth: 320 }}
        />
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Device</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Enabled</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {tokens.items.map((token) => (
                <TableRow key={token.id} hover>
                  <TableCell>{token.auth_device}</TableCell>
                  <TableCell>{token.token_value}</TableCell>
                  <TableCell>{token.nice_name}</TableCell>
                  <TableCell>{usernameFor(token.user_id)}</TableCell>
                  <TableCell>{token.enabled ? "Yes" : "No"}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} sx={{ justifyContent: "flex-end" }}>
                      <Button
                        size="small"
                        onClick={() =>
                          setEditor({
                            token,
                            authDevice: token.auth_device,
                            tokenValue: token.token_value,
                            niceName: token.nice_name ?? "",
                            userId: token.user_id != null ? String(token.user_id) : "",
                            enabled: token.enabled ?? true,
                          })
                        }
                      >
                        Edit
                      </Button>
                      <Button size="small" color="error" onClick={() => void remove(token)}>
                        Delete
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={tokens} />
      </Stack>

      <Dialog open={editor !== null} onClose={() => setEditor(null)} fullWidth maxWidth="xs">
        <DialogTitle>{editor?.token ? "Edit token" : "Add token"}</DialogTitle>
        <DialogContent>
          {editor && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Auth device"
                value={editor.authDevice}
                onChange={(e) => setEditor({ ...editor, authDevice: e.target.value })}
                helperText='Namespace, e.g. "core.rfid" or "core.onewire"'
                required
              />
              <TextField
                label="Token value"
                value={editor.tokenValue}
                onChange={(e) => setEditor({ ...editor, tokenValue: e.target.value })}
                required
              />
              <TextField
                label="Nice name"
                value={editor.niceName}
                onChange={(e) => setEditor({ ...editor, niceName: e.target.value })}
              />
              <TextField
                select
                label="Assigned user"
                value={editor.userId}
                onChange={(e) => setEditor({ ...editor, userId: e.target.value })}
              >
                <MenuItem value="">— unassigned —</MenuItem>
                {(users.data ?? []).map((user) => (
                  <MenuItem key={user.id} value={String(user.id)}>
                    {user.username}
                  </MenuItem>
                ))}
              </TextField>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={editor.enabled}
                    onChange={(e) => setEditor({ ...editor, enabled: e.target.checked })}
                  />
                }
                label="Enabled"
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditor(null)}>Cancel</Button>
          <Button onClick={() => void save()} variant="contained" disabled={busy}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
}
