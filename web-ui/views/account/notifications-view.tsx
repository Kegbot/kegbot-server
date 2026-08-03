import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { type FormEvent, useEffect, useState } from "react";
import type { NotificationSettings } from "@/api";
import {
  accountEmailCreate,
  notificationSettingsCreate,
  notificationSettingsList,
  notificationSettingsPartialUpdate,
} from "@/api";
import { useCurrentUser } from "@/components/current-user-context";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { toErrorMessage, unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException } from "@/lib/forms";
import { useAsyncData } from "@/lib/use-async-data";

const EMAIL_BACKEND = "pykeg.notification.backends.email.EmailNotificationBackend";

const PREFS: Array<{ key: keyof NotificationSettings & string; label: string }> = [
  { key: "keg_tapped", label: "A keg is tapped" },
  { key: "session_started", label: "A new drinking session starts" },
  { key: "keg_volume_low", label: "A keg is running low" },
  { key: "keg_ended", label: "A keg is finished" },
];

function EmailPrefsSection() {
  const { showMessage } = useSnackbar();
  const existing = useAsyncData(async () => {
    const page = await unwrap(notificationSettingsList({ query: { page_size: 100 } }));
    return (page.results ?? []).find((s) => s.backend === EMAIL_BACKEND) ?? null;
  });
  const [prefs, setPrefs] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!existing.loading) {
      setPrefs({
        keg_tapped: existing.data?.keg_tapped ?? true,
        session_started: existing.data?.session_started ?? false,
        keg_volume_low: existing.data?.keg_volume_low ?? false,
        keg_ended: existing.data?.keg_ended ?? false,
      });
    }
  }, [existing.loading, existing.data]);

  const save = async () => {
    setBusy(true);
    try {
      if (existing.data) {
        await unwrap(
          notificationSettingsPartialUpdate({
            path: { id: existing.data.id },
            body: prefs,
          }),
        );
      } else {
        await unwrap(notificationSettingsCreate({ body: { backend: EMAIL_BACKEND, ...prefs } }));
      }
      showMessage("Notification settings saved.");
      existing.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card variant="outlined">
      <CardHeader title="E-mail notifications" subheader="Send me an e-mail when…" />
      <CardContent>
        <LoadingZone loading={existing.loading} error={existing.error}>
          <Stack spacing={2}>
            <FormGroup>
              {PREFS.map((pref) => (
                <FormControlLabel
                  key={pref.key}
                  control={
                    <Checkbox
                      checked={prefs[pref.key] ?? false}
                      onChange={(e) => setPrefs((p) => ({ ...p, [pref.key]: e.target.checked }))}
                    />
                  }
                  label={pref.label}
                />
              ))}
            </FormGroup>
            <Button onClick={() => void save()} variant="contained" disabled={busy}>
              Save settings
            </Button>
          </Stack>
        </LoadingZone>
      </CardContent>
    </Card>
  );
}

function ChangeEmailSection() {
  const { user } = useCurrentUser();
  const { showMessage } = useSnackbar();
  const [email, setEmail] = useState(user?.email ?? "");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(accountEmailCreate({ body: { email } }));
      showMessage(`A confirmation e-mail has been sent to ${email}.`);
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card variant="outlined">
      <CardHeader
        title="E-mail address"
        subheader="Changing your address sends a confirmation link to the new one."
      />
      <CardContent>
        <form onSubmit={onSubmit}>
          <Stack spacing={2} sx={{ maxWidth: 480 }}>
            <TextField
              label="E-mail address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={Boolean(fieldError(errors, "email"))}
              helperText={fieldError(errors, "email")}
              required
            />
            <Button type="submit" variant="outlined" disabled={busy}>
              Change e-mail
            </Button>
          </Stack>
        </form>
      </CardContent>
    </Card>
  );
}

export function NotificationsView() {
  return (
    <Page title="Notifications" hideHeading>
      <Stack spacing={3}>
        <EmailPrefsSection />
        <ChangeEmailSection />
      </Stack>
    </Page>
  );
}
