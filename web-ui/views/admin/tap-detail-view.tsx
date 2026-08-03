import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  flowMetersList,
  flowTogglesList,
  kegsList,
  tapsAttachKegCreate,
  tapsConnectMeterCreate,
  tapsConnectThermoCreate,
  tapsConnectToggleCreate,
  tapsDestroy,
  tapsEndKegCreate,
  tapsPartialUpdate,
  tapsRecordDrinkCreate,
  tapsRetrieve,
  tapsStartKegCreate,
  thermoSensorsList,
  usersList,
} from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { KegProgress } from "@/components/keg-progress";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import SHARED from "@/lib/shared-constants";
import { useAsyncData } from "@/lib/use-async-data";

function useAction(onDone: () => void) {
  const { showMessage } = useSnackbar();
  const [busy, setBusy] = useState(false);
  const run = async (action: () => Promise<unknown>, successMessage: string) => {
    setBusy(true);
    try {
      await action();
      showMessage(successMessage);
      onDone();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };
  return { busy, run };
}

export function TapDetailView() {
  const params = useParams();
  const tapId = Number(params.id);
  const navigate = useNavigate();
  const confirm = useConfirm();

  const tap = useAsyncData(() => unwrap(tapsRetrieve({ path: { id: tapId } })), {
    deps: [tapId],
  });
  const { busy, run } = useAction(() => tap.reload());

  const availableKegs = useAsyncData(
    async () =>
      (await unwrap(kegsList({ query: { status: "available", page_size: 100 } }))).results ?? [],
    { deps: [tap.data?.current_keg_id ?? null] },
  );
  const meters = useAsyncData(
    async () => (await unwrap(flowMetersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const toggles = useAsyncData(
    async () => (await unwrap(flowTogglesList({ query: { page_size: 100 } }))).results ?? [],
  );
  const sensors = useAsyncData(
    async () => (await unwrap(thermoSensorsList({ query: { page_size: 100 } }))).results ?? [],
  );

  const [name, setName] = useState<string | null>(null);
  const [attachKegId, setAttachKegId] = useState("");
  const [newBeverage, setNewBeverage] = useState({ name: "", producer: "", style: "" });
  const [newKegType, setNewKegType] = useState(
    SHARED.KEG_TYPE_OTHER === "other" ? "half-barrel" : "half-barrel",
  );
  const [pour, setPour] = useState({ volume: "", username: "", shout: "", spilled: false });

  const currentKeg = tap.data?.current_keg ?? null;

  const endKeg = async () => {
    if (
      await confirm({
        title: "End this keg?",
        message: "The keg will be marked finished and detached from the tap.",
        confirmText: "End keg",
        destructive: true,
      })
    ) {
      await run(() => unwrap(tapsEndKegCreate({ path: { id: tapId } })), "Keg ended.");
    }
  };

  const deleteTap = async () => {
    if (
      await confirm({
        title: "Delete this tap?",
        confirmText: "Delete",
        destructive: true,
      })
    ) {
      try {
        await unwrap(tapsDestroy({ path: { id: tapId } }));
        navigate("/kegadmin/taps");
      } catch {
        // surfaced by snackbar in run(); simple fallback here
      }
    }
  };

  const startKeg = (event: FormEvent) => {
    event.preventDefault();
    void run(
      () =>
        unwrap(
          tapsStartKegCreate({
            path: { id: tapId },
            body: {
              beverage_name: newBeverage.name,
              producer_name: newBeverage.producer,
              style_name: newBeverage.style,
              keg_type: newKegType as never,
            },
          }),
        ),
      "New keg started.",
    );
  };

  const recordDrink = (event: FormEvent) => {
    event.preventDefault();
    void run(
      () =>
        unwrap(
          tapsRecordDrinkCreate({
            path: { id: tapId },
            body: {
              volume_ml: Number(pour.volume),
              username: pour.username,
              shout: pour.shout,
              spilled: pour.spilled,
            },
          }),
        ),
      pour.spilled ? "Spill recorded." : "Drink recorded.",
    );
  };

  const usernames = useAsyncData(
    async () => (await unwrap(usersList({ query: { page_size: 100 } }))).results ?? [],
  );

  return (
    <Page title={tap.data?.name ?? "Tap"} loading={tap.loading} error={tap.error}>
      {tap.data && (
        <Stack spacing={3}>
          <Card variant="outlined">
            <CardHeader title="Current keg" />
            <CardContent>
              {currentKeg ? (
                <Stack spacing={2}>
                  <Typography variant="h6">
                    {currentKeg.beverage.name}{" "}
                    <Typography component="span" color="text.secondary">
                      ({currentKeg.beverage.producer.name})
                    </Typography>
                  </Typography>
                  <KegProgress keg={currentKeg} />
                  <Stack direction="row" spacing={2}>
                    <Button
                      color="error"
                      variant="outlined"
                      onClick={() => void endKeg()}
                      disabled={busy}
                    >
                      End keg
                    </Button>
                  </Stack>
                </Stack>
              ) : (
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Stack spacing={2}>
                      <Typography variant="subtitle1">Attach an existing keg</Typography>
                      <TextField
                        select
                        label="Available kegs"
                        value={attachKegId}
                        onChange={(e) => setAttachKegId(e.target.value)}
                        size="small"
                      >
                        {(availableKegs.data ?? []).map((keg) => (
                          <MenuItem key={keg.id} value={String(keg.id)}>
                            #{keg.id} — {keg.beverage.name}
                          </MenuItem>
                        ))}
                      </TextField>
                      <Button
                        variant="contained"
                        disabled={busy || !attachKegId}
                        onClick={() =>
                          void run(
                            () =>
                              unwrap(
                                tapsAttachKegCreate({
                                  path: { id: tapId },
                                  body: { keg_id: Number(attachKegId) },
                                }),
                              ),
                            "Keg attached.",
                          )
                        }
                      >
                        Attach keg
                      </Button>
                    </Stack>
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <form onSubmit={startKeg}>
                      <Stack spacing={2}>
                        <Typography variant="subtitle1">…or start a brand-new keg</Typography>
                        <TextField
                          label="Beverage name"
                          value={newBeverage.name}
                          onChange={(e) => setNewBeverage({ ...newBeverage, name: e.target.value })}
                          size="small"
                          required
                        />
                        <TextField
                          label="Producer"
                          value={newBeverage.producer}
                          onChange={(e) =>
                            setNewBeverage({ ...newBeverage, producer: e.target.value })
                          }
                          size="small"
                          required
                        />
                        <TextField
                          label="Style"
                          value={newBeverage.style}
                          onChange={(e) =>
                            setNewBeverage({ ...newBeverage, style: e.target.value })
                          }
                          size="small"
                          required
                        />
                        <TextField
                          select
                          label="Keg size"
                          value={newKegType}
                          onChange={(e) => setNewKegType(e.target.value)}
                          size="small"
                        >
                          {Object.entries(SHARED.KEG_TYPES).map(([value, label]) => (
                            <MenuItem key={value} value={value}>
                              {label}
                            </MenuItem>
                          ))}
                        </TextField>
                        <Button type="submit" variant="contained" disabled={busy}>
                          Start keg
                        </Button>
                      </Stack>
                    </form>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>

          {currentKeg && (
            <Card variant="outlined">
              <CardHeader
                title="Record a drink"
                subheader="Manually log a pour (or spill) against the current keg."
              />
              <CardContent>
                <form onSubmit={recordDrink}>
                  <Stack
                    direction="row"
                    spacing={2}
                    sx={{ flexWrap: "wrap", alignItems: "center" }}
                  >
                    <TextField
                      label="Volume (mL)"
                      type="number"
                      value={pour.volume}
                      onChange={(e) => setPour({ ...pour, volume: e.target.value })}
                      size="small"
                      required
                    />
                    <TextField
                      select
                      label="Drinker"
                      value={pour.username}
                      onChange={(e) => setPour({ ...pour, username: e.target.value })}
                      size="small"
                      sx={{ minWidth: 160 }}
                    >
                      <MenuItem value="">guest</MenuItem>
                      {(usernames.data ?? []).map((user) => (
                        <MenuItem key={user.id} value={user.username}>
                          {user.username}
                        </MenuItem>
                      ))}
                    </TextField>
                    <TextField
                      label="Shout"
                      value={pour.shout}
                      onChange={(e) => setPour({ ...pour, shout: e.target.value })}
                      size="small"
                    />
                    <TextField
                      select
                      label="Type"
                      value={pour.spilled ? "spill" : "drink"}
                      onChange={(e) => setPour({ ...pour, spilled: e.target.value === "spill" })}
                      size="small"
                    >
                      <MenuItem value="drink">Drink</MenuItem>
                      <MenuItem value="spill">Spill</MenuItem>
                    </TextField>
                    <Button type="submit" variant="contained" disabled={busy}>
                      Record
                    </Button>
                  </Stack>
                </form>
              </CardContent>
            </Card>
          )}

          <Card variant="outlined">
            <CardHeader title="Hardware connections" />
            <CardContent>
              <Stack spacing={2} sx={{ maxWidth: 480 }}>
                <TextField
                  select
                  label="Flow meter"
                  value={String(meters.data?.find((m) => m.tap_id === tapId)?.id ?? "")}
                  onChange={(e) =>
                    void run(
                      () =>
                        unwrap(
                          tapsConnectMeterCreate({
                            path: { id: tapId },
                            body: { meter_id: e.target.value ? Number(e.target.value) : null },
                          }),
                        ),
                      "Meter connection updated.",
                    )
                  }
                  size="small"
                >
                  <MenuItem value="">— not connected —</MenuItem>
                  {(meters.data ?? []).map((meter) => (
                    <MenuItem key={meter.id} value={String(meter.id)}>
                      Meter #{meter.id} (port {meter.port_name})
                    </MenuItem>
                  ))}
                </TextField>
                <TextField
                  select
                  label="Flow toggle"
                  value={String(toggles.data?.find((t) => t.tap_id === tapId)?.id ?? "")}
                  onChange={(e) =>
                    void run(
                      () =>
                        unwrap(
                          tapsConnectToggleCreate({
                            path: { id: tapId },
                            body: { toggle_id: e.target.value ? Number(e.target.value) : null },
                          }),
                        ),
                      "Toggle connection updated.",
                    )
                  }
                  size="small"
                >
                  <MenuItem value="">— not connected —</MenuItem>
                  {(toggles.data ?? []).map((toggle) => (
                    <MenuItem key={toggle.id} value={String(toggle.id)}>
                      Toggle #{toggle.id} (port {toggle.port_name})
                    </MenuItem>
                  ))}
                </TextField>
                <TextField
                  select
                  label="Temperature sensor"
                  value={String(tap.data.temperature_sensor_id ?? "")}
                  onChange={(e) =>
                    void run(
                      () =>
                        unwrap(
                          tapsConnectThermoCreate({
                            path: { id: tapId },
                            body: {
                              thermo_sensor_id: e.target.value ? Number(e.target.value) : null,
                            },
                          }),
                        ),
                      "Sensor connection updated.",
                    )
                  }
                  size="small"
                >
                  <MenuItem value="">— not connected —</MenuItem>
                  {(sensors.data ?? []).map((sensor) => (
                    <MenuItem key={sensor.id} value={String(sensor.id)}>
                      {sensor.nice_name || sensor.raw_name}
                    </MenuItem>
                  ))}
                </TextField>
              </Stack>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardHeader title="Tap settings" />
            <CardContent>
              <Stack direction="row" spacing={2} sx={{ alignItems: "center", maxWidth: 480 }}>
                <TextField
                  label="Name"
                  value={name ?? tap.data.name}
                  onChange={(e) => setName(e.target.value)}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <Button
                  variant="outlined"
                  disabled={busy || name === null || name === tap.data.name}
                  onClick={() =>
                    void run(
                      () =>
                        unwrap(
                          tapsPartialUpdate({ path: { id: tapId }, body: { name: name ?? "" } }),
                        ),
                      "Tap renamed.",
                    )
                  }
                >
                  Rename
                </Button>
                <Button color="error" variant="outlined" onClick={() => void deleteTap()}>
                  Delete tap
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      )}
    </Page>
  );
}
