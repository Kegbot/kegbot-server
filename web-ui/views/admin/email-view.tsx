import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { type FormEvent, useState } from "react";
import { adminEmailTestCreate } from "@/api-client";
import { FormErrorAlert } from "@/components/form-error-alert";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException } from "@/lib/forms";
import { useSiteSettings } from "@/views/admin/use-site-settings";

export function EmailView() {
  const { settings } = useSiteSettings();
  const { showMessage } = useSnackbar();
  const [address, setAddress] = useState("");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const configured =
    settings.data?.email_config?.startsWith("smtp") ||
    settings.data?.email_config?.startsWith("submission");

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(adminEmailTestCreate({ body: { address } }));
      showMessage(`Test e-mail sent to ${address}.`);
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="E-mail">
      <LoadingZone loading={settings.loading} error={settings.error}>
        <Stack spacing={2} sx={{ maxWidth: 560 }}>
          {configured ? (
            <Alert severity="success">E-mail is configured: {settings.data?.email_config}</Alert>
          ) : (
            <Alert severity="warning">
              E-mail is not configured. Set an smtp:// or submission:// URI in Advanced settings.
            </Alert>
          )}
          <form onSubmit={onSubmit}>
            <Stack spacing={2}>
              <FormErrorAlert errors={errors} fields={["address"]} />
              <Stack direction="row" spacing={2} sx={{ alignItems: "flex-start" }}>
                <TextField
                  label="Send a test e-mail to"
                  type="email"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  error={Boolean(fieldError(errors, "address"))}
                  helperText={fieldError(errors, "address")}
                  required
                  sx={{ flexGrow: 1 }}
                />
                <Button type="submit" variant="contained" disabled={busy} sx={{ mt: 1 }}>
                  Send
                </Button>
              </Stack>
            </Stack>
          </form>
        </Stack>
      </LoadingZone>
    </Page>
  );
}
