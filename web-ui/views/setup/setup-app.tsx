import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";
import Stepper from "@mui/material/Stepper";
import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import {
  setupAdminUserCreate,
  setupFinishCreate,
  setupMigrateCreate,
  setupSettingsCreate,
  setupStatusRetrieve,
  setupUpgradeCreate,
} from "@/api-client";
import { LoadingZone } from "@/components/loading-zone";
import { toErrorMessage, unwrap } from "@/lib/api";
import SHARED from "@/lib/shared-constants";
import { useAsyncData } from "@/lib/use-async-data";

const STEPS = ["Database", "Hardware", "Accounts", "Site settings", "Admin account"];

function UpgradeApp() {
  const status = useAsyncData(() => unwrap(setupStatusRetrieve()));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upgrade = async () => {
    setBusy(true);
    setError(null);
    try {
      await unwrap(setupUpgradeCreate());
      window.location.reload();
    } catch (e) {
      setError(toErrorMessage(e));
      setBusy(false);
    }
  };

  return (
    <Paper sx={{ p: 4 }}>
      <LoadingZone loading={status.loading} error={status.error}>
        <Stack spacing={2}>
          <Typography variant="h5">Upgrade required</Typography>
          <Typography color="text.secondary">
            Installed version: {status.data?.installed_version ?? "unknown"} · new version:{" "}
            {status.data?.current_version}
          </Typography>
          {error && <Alert severity="error">{error}</Alert>}
          <Button variant="contained" onClick={() => void upgrade()} disabled={busy} size="large">
            {busy ? "Upgrading…" : "Upgrade now"}
          </Button>
        </Stack>
      </LoadingZone>
    </Paper>
  );
}

function SetupWizard() {
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [migrateOutput, setMigrateOutput] = useState<string | null>(null);

  const [enableSensing, setEnableSensing] = useState(true);
  const [enableUsers, setEnableUsers] = useState(true);
  const [site, setSite] = useState({
    title: "My Kegbot",
    privacy: "public",
    timezone: "UTC",
    volume_display_units: "imperial",
    temperature_display_units: "f",
  });
  const [admin, setAdmin] = useState({ username: "admin", email: "", password: "", password2: "" });

  const runStep = async (action: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const migrate = () =>
    runStep(async () => {
      const result = (await unwrap(setupMigrateCreate())) as { output?: string };
      setMigrateOutput(result.output ?? "");
      setStep(1);
    });

  const finish = () =>
    runStep(async () => {
      if (admin.password !== admin.password2) {
        throw new Error("The two password fields didn't match.");
      }
      await unwrap(
        setupSettingsCreate({
          body: {
            title: site.title,
            privacy: site.privacy as never,
            timezone: site.timezone as never,
            volume_display_units: site.volume_display_units as never,
            temperature_display_units: site.temperature_display_units as never,
            enable_sensing: enableSensing,
            enable_users: enableUsers,
          },
        }),
      );
      await unwrap(
        setupAdminUserCreate({
          body: { username: admin.username, email: admin.email, password: admin.password },
        }),
      );
      await unwrap(setupFinishCreate());
      window.location.reload();
    });

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Welcome to Kegbot!</Typography>
      <Stepper activeStep={step} alternativeLabel>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {error && <Alert severity="error">{error}</Alert>}

      {step === 0 && (
        <Stack spacing={2}>
          <Typography>
            First, let's create (or update) the database. This may take a minute.
          </Typography>
          <Button variant="contained" onClick={() => void migrate()} disabled={busy} size="large">
            {busy ? "Working…" : "Set up database"}
          </Button>
          {migrateOutput != null && (
            <Box
              component="pre"
              sx={{ fontFamily: "monospace", fontSize: 12, whiteSpace: "pre-wrap" }}
            >
              {migrateOutput}
            </Box>
          )}
        </Stack>
      )}

      {step === 1 && (
        <Stack spacing={2}>
          <Typography>Will this Kegbot have flow-sensing hardware attached?</Typography>
          <FormControlLabel
            control={
              <Switch
                checked={enableSensing}
                onChange={(e) => setEnableSensing(e.target.checked)}
              />
            }
            label="Enable hardware sensing features"
          />
          <Button variant="contained" onClick={() => setStep(2)} sx={{ alignSelf: "flex-start" }}>
            Continue
          </Button>
        </Stack>
      )}

      {step === 2 && (
        <Stack spacing={2}>
          <Typography>Track individual drinkers with user accounts?</Typography>
          <FormControlLabel
            control={
              <Switch checked={enableUsers} onChange={(e) => setEnableUsers(e.target.checked)} />
            }
            label="Enable user pour tracking"
          />
          <Button variant="contained" onClick={() => setStep(3)} sx={{ alignSelf: "flex-start" }}>
            Continue
          </Button>
        </Stack>
      )}

      {step === 3 && (
        <Stack spacing={2}>
          <TextField
            label="Site title"
            value={site.title}
            onChange={(e) => setSite({ ...site, title: e.target.value })}
          />
          <TextField
            select
            label="Privacy"
            value={site.privacy}
            onChange={(e) => setSite({ ...site, privacy: e.target.value })}
          >
            {Object.entries(SHARED.PRIVACY_CHOICES).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Time zone"
            value={site.timezone}
            onChange={(e) => setSite({ ...site, timezone: e.target.value })}
          >
            {SHARED.TIMEZONES.map((zone) => (
              <MenuItem key={zone} value={zone}>
                {zone}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Volume units"
            value={site.volume_display_units}
            onChange={(e) => setSite({ ...site, volume_display_units: e.target.value })}
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
            value={site.temperature_display_units}
            onChange={(e) => setSite({ ...site, temperature_display_units: e.target.value })}
          >
            {Object.entries(SHARED.TEMPERATURE_DISPLAY_UNITS_CHOICES).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </TextField>
          <Button variant="contained" onClick={() => setStep(4)} sx={{ alignSelf: "flex-start" }}>
            Continue
          </Button>
        </Stack>
      )}

      {step === 4 && (
        <Stack spacing={2}>
          <Typography>Finally, create your admin account.</Typography>
          <TextField
            label="Username"
            value={admin.username}
            onChange={(e) => setAdmin({ ...admin, username: e.target.value })}
            required
          />
          <TextField
            label="E-mail"
            type="email"
            value={admin.email}
            onChange={(e) => setAdmin({ ...admin, email: e.target.value })}
            helperText="In case you lose your password."
            required
          />
          <TextField
            label="Password"
            type="password"
            value={admin.password}
            onChange={(e) => setAdmin({ ...admin, password: e.target.value })}
            required
          />
          <TextField
            label="Password (again)"
            type="password"
            value={admin.password2}
            onChange={(e) => setAdmin({ ...admin, password2: e.target.value })}
            required
          />
          <Button
            variant="contained"
            onClick={() => void finish()}
            disabled={busy}
            size="large"
            sx={{ alignSelf: "flex-start" }}
          >
            {busy ? "Finishing…" : "Finish setup"}
          </Button>
        </Stack>
      )}
    </Stack>
  );
}

/** Full-page setup/upgrade flow, rendered instead of the app. */
export function SetupApp({ kind }: { kind: "setup_required" | "upgrade_required" }) {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Container maxWidth="md" sx={{ py: 6 }}>
        {kind === "upgrade_required" ? <UpgradeApp /> : <SetupWizard />}
      </Container>
    </Box>
  );
}
