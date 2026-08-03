import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { authRegisterCreate } from "@/api";
import { useConfig } from "@/components/config-context";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException, nonFieldErrors } from "@/lib/forms";

const FIELDS = ["username", "email", "password"];

export function RegisterView() {
  const { me, refresh } = useConfig();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const inviteCode = params.get("invite_code") || "";

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const inviteNeeded = me.site.registration_mode !== "public" && !inviteCode;

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (password !== password2) {
      setErrors({ password: ["The two password fields didn't match."] });
      return;
    }
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(
        authRegisterCreate({
          body: { username, email, password, invite_code: inviteCode || undefined },
        }),
      );
      await refresh();
      navigate("/", { replace: true });
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  if (inviteNeeded) {
    return (
      <Paper sx={{ p: 4 }}>
        <Stack spacing={2}>
          <Typography variant="h5">Invitation required</Typography>
          <Alert severity="info">
            New accounts on this site are invitation-only. Ask a member for an invitation, then
            follow the link in the invitation e-mail.
          </Alert>
        </Stack>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 4 }}>
      <form onSubmit={onSubmit}>
        <Stack spacing={2}>
          <Typography variant="h5">Create an account</Typography>
          {nonFieldErrors(errors, FIELDS).map((message) => (
            <Alert key={message} severity="error">
              {message}
            </Alert>
          ))}
          <TextField
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            error={Boolean(fieldError(errors, "username"))}
            helperText={fieldError(errors, "username")}
            autoFocus
            required
          />
          <TextField
            label="E-mail address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={Boolean(fieldError(errors, "email"))}
            helperText={fieldError(errors, "email")}
            required
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={Boolean(fieldError(errors, "password"))}
            helperText={fieldError(errors, "password")}
            autoComplete="new-password"
            required
          />
          <TextField
            label="Password (again)"
            type="password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            autoComplete="new-password"
            required
          />
          <Button type="submit" variant="contained" disabled={busy} size="large">
            Register
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
