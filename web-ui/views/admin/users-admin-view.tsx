import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Menu from "@mui/material/Menu";
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
import type { User } from "@/api-client";
import { usersCreate, usersList, usersPartialUpdate, usersSetPasswordCreate } from "@/api-client";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { UserLink } from "@/components/user-link";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useCursorList } from "@/lib/use-cursor-list";

function UserActions({ user, onChanged }: { user: User; onChanged: () => void }) {
  const { showMessage } = useSnackbar();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);

  const patch = async (body: Record<string, unknown>, message: string) => {
    setAnchor(null);
    try {
      await unwrap(usersPartialUpdate({ path: { username: user.username }, body: body as never }));
      showMessage(message);
      onChanged();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  const setPassword = async () => {
    setAnchor(null);
    const password = window.prompt(`New password for ${user.username}:`);
    if (!password) {
      return;
    }
    try {
      await unwrap(
        usersSetPasswordCreate({ path: { username: user.username }, body: { password } }),
      );
      showMessage("Password updated.");
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  if (user.username === "guest") {
    return null;
  }

  return (
    <>
      <Button size="small" onClick={(e) => setAnchor(e.currentTarget)}>
        Actions
      </Button>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}>
        {user.is_active ? (
          <MenuItem onClick={() => void patch({ is_active: false }, "Account disabled.")}>
            Disable account
          </MenuItem>
        ) : (
          <MenuItem onClick={() => void patch({ is_active: true }, "Account enabled.")}>
            Enable account
          </MenuItem>
        )}
        {user.is_staff ? (
          <MenuItem onClick={() => void patch({ is_staff: false }, "Staff access revoked.")}>
            Revoke staff
          </MenuItem>
        ) : (
          <MenuItem onClick={() => void patch({ is_staff: true }, "Staff access granted.")}>
            Grant staff
          </MenuItem>
        )}
        <MenuItem onClick={() => void setPassword()}>Set password…</MenuItem>
      </Menu>
    </>
  );
}

export function UsersAdminView() {
  const { showMessage } = useSnackbar();
  const [search, setSearch] = useState("");
  const users = useCursorList(
    (cursor) => unwrap(usersList({ query: { cursor, search: search || undefined } })),
    [search],
  );

  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ username: "", email: "", password: "", isStaff: false });
  const [busy, setBusy] = useState(false);

  const create = async () => {
    setBusy(true);
    try {
      await unwrap(
        usersCreate({
          body: {
            username: form.username,
            email: form.email,
            password: form.password,
            is_staff: form.isStaff,
          },
        }),
      );
      showMessage(`User ${form.username} created.`);
      setCreating(false);
      setForm({ username: "", email: "", password: "", isStaff: false });
      users.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page
      title="Users"
      loading={users.loading}
      error={users.error}
      headerRight={
        <Button variant="contained" onClick={() => setCreating(true)}>
          Add user
        </Button>
      }
    >
      <Stack spacing={2}>
        <TextField
          label="Search users"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          sx={{ maxWidth: 320 }}
        />
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Display name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {users.items
                .filter((user) => user.username !== "guest")
                .map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <UserLink user={user} />
                    </TableCell>
                    <TableCell>{user.display_name}</TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={1}>
                        {!user.is_active && <Chip size="small" label="disabled" />}
                        {user.is_staff && <Chip size="small" color="primary" label="staff" />}
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <UserActions user={user} onChanged={users.reload} />
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={users} />
      </Stack>

      <Dialog open={creating} onClose={() => setCreating(false)} fullWidth maxWidth="xs">
        <DialogTitle>Add user</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
            <TextField
              label="E-mail"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <TextField
              label="Password"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={form.isStaff}
                  onChange={(e) => setForm({ ...form, isStaff: e.target.checked })}
                />
              }
              label="Staff (admin access)"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreating(false)}>Cancel</Button>
          <Button onClick={() => void create()} variant="contained" disabled={busy}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
}
