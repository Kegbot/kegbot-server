import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { type FormEvent, useState } from "react";
import { accountPasswordCreate } from "@/api-client";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException, nonFieldErrors } from "@/lib/forms";

const FIELDS = ["current_password", "new_password"];

export function PasswordView() {
  const { showMessage } = useSnackbar();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPassword2, setNewPassword2] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (newPassword !== newPassword2) {
      setErrors({ new_password: ["The two password fields didn't match."] });
      return;
    }
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(
        accountPasswordCreate({
          body: { current_password: currentPassword, new_password: newPassword },
        }),
      );
      showMessage("Password changed.");
      setCurrentPassword("");
      setNewPassword("");
      setNewPassword2("");
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="Change Password" hideHeading>
      <form onSubmit={onSubmit}>
        <Stack spacing={2} sx={{ maxWidth: 480 }}>
          {nonFieldErrors(errors, FIELDS).map((message) => (
            <Alert key={message} severity="error">
              {message}
            </Alert>
          ))}
          <TextField
            label="Current password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            error={Boolean(fieldError(errors, "current_password"))}
            helperText={fieldError(errors, "current_password")}
            autoComplete="current-password"
            required
          />
          <TextField
            label="New password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            error={Boolean(fieldError(errors, "new_password"))}
            helperText={fieldError(errors, "new_password")}
            autoComplete="new-password"
            required
          />
          <TextField
            label="New password (again)"
            type="password"
            value={newPassword2}
            onChange={(e) => setNewPassword2(e.target.value)}
            autoComplete="new-password"
            required
          />
          <Button type="submit" variant="contained" disabled={busy}>
            Change password
          </Button>
        </Stack>
      </form>
    </Page>
  );
}
