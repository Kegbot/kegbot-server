import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { type FormEvent, useState } from "react";
import { accountMugshotCreate, usersMePartialUpdate } from "@/api-client";
import { useCurrentUser } from "@/components/current-user-context";
import { FormErrorAlert } from "@/components/form-error-alert";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { toErrorMessage, unwrap } from "@/lib/api";
import { fieldError, formErrorsFromException } from "@/lib/forms";

export function ProfileView() {
  const { user, refresh } = useCurrentUser();
  const { showMessage } = useSnackbar();
  const [displayName, setDisplayName] = useState(user?.display_name ?? "");
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(usersMePartialUpdate({ body: { display_name: displayName } }));
      await refresh();
      showMessage("Profile updated.");
    } catch (error) {
      setErrors(formErrorsFromException(error));
    } finally {
      setBusy(false);
    }
  };

  const onMugshot = async (file: File | undefined) => {
    if (!file) {
      return;
    }
    setBusy(true);
    try {
      await unwrap(accountMugshotCreate({ body: { image: file } }));
      await refresh();
      showMessage("Mugshot updated.");
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="Profile" hideHeading>
      <Stack spacing={3} sx={{ maxWidth: 480 }}>
        <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
          <Avatar src={user?.picture?.resized_url ?? undefined} sx={{ width: 80, height: 80 }}>
            {(user?.display_name || user?.username || "?").charAt(0).toUpperCase()}
          </Avatar>
          <Button component="label" variant="outlined" disabled={busy}>
            Change mugshot
            <input
              hidden
              type="file"
              accept="image/*"
              onChange={(e) => void onMugshot(e.target.files?.[0])}
            />
          </Button>
        </Stack>
        <form onSubmit={onSubmit}>
          <Stack spacing={2}>
            <FormErrorAlert errors={errors} fields={["display_name"]} />
            <TextField
              label="Display name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              error={Boolean(fieldError(errors, "display_name"))}
              helperText={
                fieldError(errors, "display_name") ??
                "Shown in some places instead of your username."
              }
            />
            <Button type="submit" variant="contained" disabled={busy}>
              Save
            </Button>
          </Stack>
        </form>
      </Stack>
    </Page>
  );
}
