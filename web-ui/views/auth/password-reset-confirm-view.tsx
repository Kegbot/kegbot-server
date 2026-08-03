import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { Link, useParams } from "react-router";
import { authPasswordResetConfirmCreate } from "@/api-client";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException, nonFieldErrors } from "@/lib/forms";

/**
 * Splits the `uidb64-token` path segment. The token is always the last
 * two dash-separated groups (Django's `<timestamp>-<hash>` format); the
 * uid is everything before them.
 */
export function splitResetParam(combined: string): { uid: string; token: string } | null {
  const parts = combined.split("-");
  if (parts.length < 3) {
    return null;
  }
  return {
    uid: parts.slice(0, -2).join("-"),
    token: parts.slice(-2).join("-"),
  };
}

export function PasswordResetConfirmView() {
  const { combined = "" } = useParams();
  const parsed = splitResetParam(combined);

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  if (!parsed) {
    return (
      <Paper sx={{ p: 4 }}>
        <Alert severity="error">This password reset link is not valid.</Alert>
      </Paper>
    );
  }

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (password !== password2) {
      setErrors({ new_password: ["The two password fields didn't match."] });
      return;
    }
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(
        authPasswordResetConfirmCreate({
          body: { uid: parsed.uid, token: parsed.token, new_password: password },
        }),
      );
      setDone(true);
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      {done ? (
        <Stack spacing={2}>
          <Typography variant="h5">Password updated</Typography>
          <Alert severity="success">Your password has been changed.</Alert>
          <Button component={Link} to="/accounts/login" variant="contained">
            Log in
          </Button>
        </Stack>
      ) : (
        <form onSubmit={onSubmit}>
          <Stack spacing={2}>
            <Typography variant="h5">Choose a new password</Typography>
            {nonFieldErrors(errors, ["new_password"]).map((message) => (
              <Alert key={message} severity="error">
                {message}
              </Alert>
            ))}
            <TextField
              label="New password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={Boolean(fieldError(errors, "new_password"))}
              helperText={fieldError(errors, "new_password")}
              autoComplete="new-password"
              autoFocus
              required
            />
            <TextField
              label="New password (again)"
              type="password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              autoComplete="new-password"
              required
            />
            <Button type="submit" variant="contained" disabled={busy} size="large">
              Set password
            </Button>
          </Stack>
        </form>
      )}
    </Paper>
  );
}
