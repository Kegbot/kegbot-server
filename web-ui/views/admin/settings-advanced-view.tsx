import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useEffect, useState } from "react";
import { siteBackgroundImageCreate } from "@/api";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { fieldError } from "@/lib/forms";
import { useSiteSettings } from "@/views/admin/use-site-settings";

export function SettingsAdvancedView() {
  const { settings, save, busy, errors } = useSiteSettings();
  const { showMessage } = useSnackbar();
  const [sessionTimeout, setSessionTimeout] = useState("180");
  const [analyticsId, setAnalyticsId] = useState("");
  const [emailConfig, setEmailConfig] = useState("");
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (settings.data) {
      setSessionTimeout(String(settings.data.session_timeout_minutes ?? 180));
      setAnalyticsId(settings.data.google_analytics_id ?? "");
      setEmailConfig(settings.data.email_config ?? "");
    }
  }, [settings.data]);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void save({
      session_timeout_minutes: Number(sessionTimeout),
      google_analytics_id: analyticsId || null,
      email_config: emailConfig,
    });
  };

  const onBackground = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    setUploading(true);
    try {
      await unwrap(siteBackgroundImageCreate({ body: { image: file } }));
      showMessage("Background image updated.");
      settings.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Page title="Advanced Settings">
      <LoadingZone loading={settings.loading} error={settings.error}>
        <form onSubmit={onSubmit}>
          <Stack spacing={2} sx={{ maxWidth: 560 }}>
            <TextField
              label="Session timeout (minutes)"
              type="number"
              value={sessionTimeout}
              onChange={(e) => setSessionTimeout(e.target.value)}
              error={Boolean(fieldError(errors, "session_timeout_minutes"))}
              helperText={
                fieldError(errors, "session_timeout_minutes") ??
                "Idle time before a drinking session is considered finished."
              }
            />
            <TextField
              label="Google Analytics ID"
              value={analyticsId}
              onChange={(e) => setAnalyticsId(e.target.value)}
              error={Boolean(fieldError(errors, "google_analytics_id"))}
              helperText={fieldError(errors, "google_analytics_id")}
            />
            <TextField
              label="E-mail configuration"
              value={emailConfig}
              onChange={(e) => setEmailConfig(e.target.value)}
              error={Boolean(fieldError(errors, "email_config"))}
              helperText={
                fieldError(errors, "email_config") ??
                "URI like smtp://user:pass@host:port or console:"
              }
            />
            <Button type="submit" variant="contained" disabled={busy}>
              Save settings
            </Button>
            <Typography variant="h6" sx={{ pt: 2 }}>
              Background image
            </Typography>
            <Button
              component="label"
              variant="outlined"
              disabled={uploading}
              sx={{ maxWidth: 240 }}
            >
              Upload background
              <input
                hidden
                type="file"
                accept="image/*"
                onChange={(e) => void onBackground(e.target.files?.[0])}
              />
            </Button>
          </Stack>
        </form>
      </LoadingZone>
    </Page>
  );
}
