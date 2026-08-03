import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { useConfig } from "@/components/config-context";
import { useCurrentUser } from "@/components/current-user-context";
import type { FormErrors } from "@/lib/api";
import { fieldError, formErrorsFromException, nonFieldErrors } from "@/lib/forms";

export function LoginView() {
  const { me } = useConfig();
  const { login, isLoggedIn } = useCurrentUser();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const next = params.get("next") || "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  useEffect(() => {
    if (isLoggedIn) {
      navigate(next, { replace: true });
    }
  }, [isLoggedIn, navigate, next]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await login(username, password);
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  if (me.sso_login_url) {
    const redir = encodeURIComponent(window.location.origin + next);
    return (
      <Paper sx={{ p: 4, textAlign: "center" }}>
        <Stack spacing={2}>
          <Typography variant="h5">Log in</Typography>
          <Button variant="contained" href={`${me.sso_login_url}?redir=${redir}`}>
            Log in with SSO
          </Button>
        </Stack>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 4 }}>
      <form onSubmit={onSubmit}>
        <Stack spacing={2}>
          <Typography variant="h5">Log in</Typography>
          {nonFieldErrors(errors, ["username", "password"]).map((message) => (
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
            autoComplete="username"
            required
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={Boolean(fieldError(errors, "password"))}
            helperText={fieldError(errors, "password")}
            autoComplete="current-password"
            required
          />
          <Button type="submit" variant="contained" disabled={busy} size="large">
            Log in
          </Button>
          <Stack direction="row" spacing={2} sx={{ justifyContent: "space-between" }}>
            {me.site.registration_mode === "public" && (
              <Button component={Link} to="/accounts/register" size="small">
                Create an account
              </Button>
            )}
            <Button component={Link} to="/accounts/password/reset" size="small">
              Forgot password?
            </Button>
          </Stack>
        </Stack>
      </form>
    </Paper>
  );
}
