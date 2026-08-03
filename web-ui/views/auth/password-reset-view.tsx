import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { authPasswordResetCreate } from "@/api";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException } from "@/lib/forms";

export function PasswordResetView() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(authPasswordResetCreate({ body: { email } }));
      setSent(true);
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      {sent ? (
        <Stack spacing={2}>
          <Typography variant="h5">Check your e-mail</Typography>
          <Alert severity="success">
            If an account exists for {email}, a password reset link is on its way.
          </Alert>
        </Stack>
      ) : (
        <form onSubmit={onSubmit}>
          <Stack spacing={2}>
            <Typography variant="h5">Reset your password</Typography>
            <TextField
              label="E-mail address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={Boolean(fieldError(errors, "email"))}
              helperText={fieldError(errors, "email")}
              autoFocus
              required
            />
            <Button type="submit" variant="contained" disabled={busy} size="large">
              Send reset link
            </Button>
          </Stack>
        </form>
      )}
    </Paper>
  );
}
