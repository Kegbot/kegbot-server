import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useParams } from "react-router";
import { accountConfirmEmailCreate } from "@/api";
import { useConfig } from "@/components/config-context";
import { useCurrentUser } from "@/components/current-user-context";
import { toErrorMessage, unwrap } from "@/lib/api";

export function ConfirmEmailView() {
  const { token = "" } = useParams();
  const { refresh } = useConfig();
  const { isLoggedIn } = useCurrentUser();
  const location = useLocation();

  const [state, setState] = useState<"working" | "done" | "error">("working");
  const [message, setMessage] = useState("");
  const started = useRef(false);

  useEffect(() => {
    if (!isLoggedIn || started.current) {
      return;
    }
    started.current = true;
    (async () => {
      try {
        await unwrap(accountConfirmEmailCreate({ body: { token } }));
        await refresh();
        setState("done");
      } catch (error) {
        setMessage(toErrorMessage(error));
        setState("error");
      }
    })();
  }, [isLoggedIn, token, refresh]);

  if (!isLoggedIn) {
    return (
      <Paper sx={{ p: 4 }}>
        <Stack spacing={2}>
          <Typography variant="h5">Confirm e-mail change</Typography>
          <Alert severity="info">Log in to confirm your new e-mail address.</Alert>
          <Button
            component={Link}
            to={`/accounts/login?next=${encodeURIComponent(location.pathname)}`}
            variant="contained"
          >
            Log in
          </Button>
        </Stack>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 4 }}>
      <Stack spacing={2}>
        <Typography variant="h5">Confirm e-mail change</Typography>
        {state === "working" && <Alert severity="info">Confirming…</Alert>}
        {state === "done" && (
          <>
            <Alert severity="success">Your e-mail address has been updated.</Alert>
            <Button component={Link} to="/account" variant="contained">
              Back to my account
            </Button>
          </>
        )}
        {state === "error" && <Alert severity="error">{message}</Alert>}
      </Stack>
    </Paper>
  );
}
