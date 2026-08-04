import Autocomplete from "@mui/material/Autocomplete";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import { type FormEvent, useEffect, useState } from "react";
import { FormErrorAlert } from "@/components/form-error-alert";
import { LoadingZone } from "@/components/loading-zone";
import { Page } from "@/components/page";
import { fieldError } from "@/lib/forms";
import SHARED from "@/lib/shared-constants";
import { useSiteSettings } from "@/views/admin/use-site-settings";

const TIMEZONES = SHARED.TIMEZONES as readonly string[];

export function SettingsLocationView() {
  const { settings, save, busy, errors } = useSiteSettings();
  const [volumeUnits, setVolumeUnits] = useState("imperial");
  const [temperatureUnits, setTemperatureUnits] = useState("f");
  const [timezone, setTimezone] = useState("UTC");

  useEffect(() => {
    if (settings.data) {
      setVolumeUnits(settings.data.volume_display_units ?? "imperial");
      setTemperatureUnits(settings.data.temperature_display_units ?? "f");
      setTimezone(settings.data.timezone ?? "UTC");
    }
  }, [settings.data]);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void save({
      volume_display_units: volumeUnits as never,
      temperature_display_units: temperatureUnits as never,
      timezone: timezone as never,
    });
  };

  return (
    <Page title="Location Settings">
      <LoadingZone loading={settings.loading} error={settings.error}>
        <form onSubmit={onSubmit}>
          <Stack spacing={2} sx={{ maxWidth: 560 }}>
            <FormErrorAlert
              errors={errors}
              fields={["volume_display_units", "temperature_display_units", "timezone"]}
            />
            <TextField
              select
              label="Volume units"
              value={volumeUnits}
              onChange={(e) => setVolumeUnits(e.target.value)}
            >
              {Object.entries(SHARED.VOLUME_DISPLAY_UNITS_CHOICES).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Temperature units"
              value={temperatureUnits}
              onChange={(e) => setTemperatureUnits(e.target.value)}
            >
              {Object.entries(SHARED.TEMPERATURE_DISPLAY_UNITS_CHOICES).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <Autocomplete
              options={TIMEZONES}
              value={timezone}
              onChange={(_, value) => setTimezone(value ?? "UTC")}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Time zone"
                  error={Boolean(fieldError(errors, "timezone"))}
                  helperText={fieldError(errors, "timezone")}
                />
              )}
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
