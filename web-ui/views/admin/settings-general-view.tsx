import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import { type FormEvent, useEffect, useState } from "react";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { fieldError, nonFieldErrors } from "@/lib/forms";
import SHARED from "@/lib/shared-constants";
import { useSiteSettings } from "@/views/admin/use-site-settings";

export function SettingsGeneralView() {
  const { settings, save, busy, errors } = useSiteSettings();
  const [title, setTitle] = useState("");
  const [privacy, setPrivacy] = useState("public");
  const [registrationMode, setRegistrationMode] = useState("public");
  const [enableSensing, setEnableSensing] = useState(true);
  const [enableUsers, setEnableUsers] = useState(true);

  useEffect(() => {
    if (settings.data) {
      setTitle(settings.data.title ?? "");
      setPrivacy(settings.data.privacy ?? "public");
      setRegistrationMode(settings.data.registration_mode ?? "public");
      setEnableSensing(settings.data.enable_sensing ?? true);
      setEnableUsers(settings.data.enable_users ?? true);
    }
  }, [settings.data]);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void save({
      title,
      privacy: privacy as never,
      registration_mode: registrationMode as never,
      enable_sensing: enableSensing,
      enable_users: enableUsers,
    });
  };

  return (
    <Page title="General Settings">
      <LoadingZone loading={settings.loading} error={settings.error}>
        <form onSubmit={onSubmit}>
          <Stack spacing={2} sx={{ maxWidth: 560 }}>
            {nonFieldErrors(errors, ["title", "privacy", "registration_mode"]).map((message) => (
              <Alert key={message} severity="error">
                {message}
              </Alert>
            ))}
            <TextField
              label="Site title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              error={Boolean(fieldError(errors, "title"))}
              helperText={fieldError(errors, "title")}
            />
            <TextField
              select
              label="Privacy"
              value={privacy}
              onChange={(e) => setPrivacy(e.target.value)}
              helperText="Who can view this site?"
            >
              {Object.entries(SHARED.PRIVACY_CHOICES).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Registration mode"
              value={registrationMode}
              onChange={(e) => setRegistrationMode(e.target.value)}
              helperText="Who can create accounts?"
            >
              {Object.entries(SHARED.REGISTRATION_MODE_CHOICES).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <FormControlLabel
              control={
                <Switch
                  checked={enableSensing}
                  onChange={(e) => setEnableSensing(e.target.checked)}
                />
              }
              label="Enable hardware sensing features"
            />
            <FormControlLabel
              control={
                <Switch checked={enableUsers} onChange={(e) => setEnableUsers(e.target.checked)} />
              }
              label="Enable user pour tracking"
            />
            <Button type="submit" variant="contained" disabled={busy}>
              Save settings
            </Button>
          </Stack>
        </form>
      </LoadingZone>
    </Page>
  );
}
