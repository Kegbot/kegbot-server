import { useState } from "react";
import type { PatchedSiteSettingsRequest } from "@/api-client";
import { sitePartialUpdate, siteRetrieve } from "@/api-client";
import { useConfig } from "@/components/config-context";
import { useSnackbar } from "@/components/snackbar-context";
import type { FormErrors } from "@/lib/api";
import { unwrap } from "@/lib/api";
import { formErrorsFromException } from "@/lib/forms";
import { useAsyncData } from "@/lib/use-async-data";

/** Loads /api/site and provides a save helper for the settings views. */
export function useSiteSettings() {
  const { refresh } = useConfig();
  const { showMessage } = useSnackbar();
  const settings = useAsyncData(() => unwrap(siteRetrieve()));
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<FormErrors | null>(null);

  const save = async (patch: PatchedSiteSettingsRequest) => {
    setBusy(true);
    setErrors(null);
    try {
      await unwrap(sitePartialUpdate({ body: patch }));
      await refresh();
      settings.reload();
      showMessage("Settings saved.");
      return true;
    } catch (error) {
      setErrors(formErrorsFromException(error));
      return false;
    } finally {
      setBusy(false);
    }
  };

  return { settings, save, busy, errors };
}
