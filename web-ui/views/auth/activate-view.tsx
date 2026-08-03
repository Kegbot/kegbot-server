import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { accountActivateCreate } from "@/api-client";
import { useConfig } from "@/components/config-context";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException, nonFieldErrors } from "@/lib/forms";

export function ActivateView() {
  const { key = "" } = useParams();
  const { refresh } = useConfig();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (password !== password2) {
      setErrors({ password: ["The two password fields didn't match."] });
      return;
    }
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(accountActivateCreate({ body: { activation_key: key, password } }));
      await refresh();
      navigate("/account", { replace: true });
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <form onSubmit={onSubmit}>
        <Stack spacing={2}>
          <Typography variant="h5">Activate your account</Typography>
          <Typography color="text.secondary">
            Choose a password to finish setting up your account.
          </Typography>
          {nonFieldErrors(errors, ["password", "activation_key"]).map((message) => (
            <Alert key={message} severity="error">
              {message}
            </Alert>
          ))}
          {fieldError(errors, "activation_key") && (
            <Alert severity="error">{fieldError(errors, "activation_key")}</Alert>
          )}
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={Boolean(fieldError(errors, "password"))}
            helperText={fieldError(errors, "password")}
            autoComplete="new-password"
            autoFocus
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
            Activate account
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}
