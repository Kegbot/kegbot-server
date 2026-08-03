import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { accountRegenerateApiKeyCreate, apiKeysList } from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { useCurrentUser } from "@/components/current-user-context";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

function ApiKeySection() {
  const confirm = useConfirm();
  const { showMessage } = useSnackbar();
  const [busy, setBusy] = useState(false);
  const keys = useAsyncData(async () => (await unwrap(apiKeysList())).results ?? []);

  const regenerate = async () => {
    if (
      !(await confirm({
        title: "Regenerate API key?",
        message: "Devices using the current key will stop working.",
        confirmText: "Regenerate",
        destructive: true,
      }))
    ) {
      return;
    }
    setBusy(true);
    try {
      await unwrap(accountRegenerateApiKeyCreate());
      showMessage("API key regenerated.");
      keys.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card variant="outlined">
      <CardHeader
        title="API key"
        subheader="Used by kegbot-pycore and other integrations to talk to this server."
      />
      <CardContent>
        <Stack spacing={2} sx={{ maxWidth: 480 }}>
          {(keys.data ?? []).map((key) => (
            <TextField
              key={key.id}
              value={key.key ?? ""}
              label={key.description || "Key"}
              slotProps={{ input: { readOnly: true } }}
              onFocus={(e) => (e.target as HTMLInputElement).select()}
            />
          ))}
          {keys.data?.length === 0 && (
            <Typography color="text.secondary">No API key yet.</Typography>
          )}
          <Button onClick={() => void regenerate()} disabled={busy} variant="outlined">
            Regenerate key
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}

export function AccountView() {
  const { user } = useCurrentUser();

  return (
    <Page title="My Account" hideHeading>
      <Stack spacing={3}>
        <Typography variant="h4">Hello, {user?.display_name || user?.username}</Typography>
        <Typography color="text.secondary">
          Username: {user?.username}
          {user?.email ? ` · ${user.email}` : ""}
        </Typography>
        {user?.is_staff && <ApiKeySection />}
      </Stack>
    </Page>
  );
}
