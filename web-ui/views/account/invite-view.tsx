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
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { invitationsCreate, invitationsDestroy, invitationsList } from "@/api";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { toErrorMessage, unwrap } from "@/lib/api";
import { formatDate } from "@/lib/format";
import { fieldError, formErrorsFromException } from "@/lib/forms";
import { useAsyncData } from "@/lib/use-async-data";

export function InviteView() {
  const { showMessage } = useSnackbar();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);
  const invitations = useAsyncData(
    async () => (await unwrap(invitationsList({ query: { page_size: 100 } }))).results ?? [],
  );

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(invitationsCreate({ body: { for_email: email } }));
      showMessage(`Invitation mailed to ${email}.`);
      setEmail("");
      invitations.reload();
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  const revoke = async (id: number) => {
    try {
      await unwrap(invitationsDestroy({ path: { id } }));
      showMessage("Invitation revoked.");
      invitations.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page title="Invite a New Drinker" hideHeading>
      <Stack spacing={3} sx={{ maxWidth: 640 }}>
        <form onSubmit={onSubmit}>
          <Stack direction="row" spacing={2} sx={{ alignItems: "flex-start" }}>
            <TextField
              label="E-mail address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={Boolean(fieldError(errors, "for_email"))}
              helperText={fieldError(errors, "for_email")}
              required
              sx={{ flexGrow: 1 }}
            />
            <Button type="submit" variant="contained" disabled={busy} sx={{ mt: 1 }}>
              Send invitation
            </Button>
          </Stack>
        </form>
        {(invitations.data?.length ?? 0) > 0 && (
          <Stack spacing={1}>
            <Typography variant="h6">Sent invitations</Typography>
            <TableContainer sx={{ overflowX: "auto" }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>E-mail</TableCell>
                    <TableCell>Expires</TableCell>
                    <TableCell />
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(invitations.data ?? []).map((invitation) => (
                    <TableRow key={invitation.id} hover>
                      <TableCell>{invitation.for_email}</TableCell>
                      <TableCell>
                        {invitation.is_expired
                          ? "Expired"
                          : formatDate(invitation.expires_date ?? "")}
                      </TableCell>
                      <TableCell align="right">
                        <MuiLink
                          component="button"
                          type="button"
                          onClick={() => void revoke(invitation.id)}
                        >
                          Revoke
                        </MuiLink>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Stack>
        )}
      </Stack>
    </Page>
  );
}
