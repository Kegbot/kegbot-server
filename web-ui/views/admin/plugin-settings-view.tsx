import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { adminPluginsSettingsRetrieve, adminPluginsSettingsUpdate } from "@/api";
import { useConfig } from "@/components/config-context";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

/**
 * Generic plugin settings editor: renders one field per key in the
 * plugin's settings dict (the webhook plugin has a single URL list).
 */
export function PluginSettingsView() {
  const params = useParams();
  const shortName = params.name ?? "";
  const { me } = useConfig();
  const { showMessage } = useSnackbar();

  const plugin = me.plugins.find((p) => p.short_name === shortName);
  const settings = useAsyncData(
    async () =>
      (await unwrap(
        adminPluginsSettingsRetrieve({ path: { short_name: shortName } }),
      )) as unknown as Record<string, string>,
    { deps: [shortName] },
  );

  const [values, setValues] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (settings.data) {
      setValues(Object.fromEntries(Object.entries(settings.data).map(([k, v]) => [k, v ?? ""])));
    }
  }, [settings.data]);

  const save = async () => {
    setBusy(true);
    try {
      await unwrap(
        adminPluginsSettingsUpdate({ path: { short_name: shortName }, body: values as never }),
      );
      showMessage("Plugin settings saved.");
      settings.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title={plugin?.name ?? shortName}>
      <LoadingZone loading={settings.loading} error={settings.error}>
        <Stack spacing={2} sx={{ maxWidth: 640 }}>
          {Object.entries(values).map(([key, value]) => (
            <TextField
              key={key}
              label={key.replaceAll("_", " ")}
              value={value}
              onChange={(e) => setValues((v) => ({ ...v, [key]: e.target.value }))}
              multiline={key.includes("urls")}
              minRows={key.includes("urls") ? 3 : 1}
              helperText={key === "webhook_urls" ? "One URL per line." : undefined}
            />
          ))}
          <Button
            onClick={() => void save()}
            variant="contained"
            disabled={busy}
            sx={{ alignSelf: "flex-start" }}
          >
            Save settings
          </Button>
        </Stack>
      </LoadingZone>
    </Page>
  );
}
