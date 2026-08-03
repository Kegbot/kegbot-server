import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import {
  controllersCreate,
  controllersDestroy,
  controllersList,
  flowMetersCreate,
  flowMetersDestroy,
  flowMetersList,
  flowTogglesCreate,
  flowTogglesDestroy,
  flowTogglesList,
} from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

export function ControllersView() {
  const { showMessage } = useSnackbar();
  const confirm = useConfirm();

  const controllers = useAsyncData(
    async () => (await unwrap(controllersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const meters = useAsyncData(
    async () => (await unwrap(flowMetersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const toggles = useAsyncData(
    async () => (await unwrap(flowTogglesList({ query: { page_size: 100 } }))).results ?? [],
  );

  const [controllerName, setControllerName] = useState("");
  const [meterForm, setMeterForm] = useState({ controllerId: "", port: "", ticksPerMl: "" });
  const [toggleForm, setToggleForm] = useState({ controllerId: "", port: "" });

  const reloadAll = () => {
    controllers.reload();
    meters.reload();
    toggles.reload();
  };

  const act = async (action: () => Promise<unknown>, message: string) => {
    try {
      await action();
      showMessage(message);
      reloadAll();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  const addController = (event: FormEvent) => {
    event.preventDefault();
    void act(
      () => unwrap(controllersCreate({ body: { name: controllerName } })),
      "Controller created.",
    ).then(() => setControllerName(""));
  };

  const removeController = async (id: number, name: string) => {
    if (
      await confirm({
        title: `Delete controller "${name}"?`,
        confirmText: "Delete",
        destructive: true,
      })
    ) {
      await act(() => unwrap(controllersDestroy({ path: { id } })), "Controller deleted.");
    }
  };

  return (
    <Page
      title="Controllers"
      loading={controllers.loading || meters.loading || toggles.loading}
      error={controllers.error ?? meters.error ?? toggles.error}
    >
      <Stack spacing={3}>
        <Card variant="outlined">
          <CardHeader title="Controllers" subheader="Physical kegboard devices." />
          <CardContent>
            <Stack spacing={2}>
              <TableContainer sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Model</TableCell>
                      <TableCell>Serial</TableCell>
                      <TableCell />
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(controllers.data ?? []).map((controller) => (
                      <TableRow key={controller.id} hover>
                        <TableCell>{controller.name}</TableCell>
                        <TableCell>{controller.model_name}</TableCell>
                        <TableCell>{controller.serial_number}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="error"
                            onClick={() => void removeController(controller.id, controller.name)}
                          >
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <form onSubmit={addController}>
                <Stack direction="row" spacing={2} sx={{ alignItems: "center", maxWidth: 480 }}>
                  <TextField
                    label="New controller name"
                    value={controllerName}
                    onChange={(e) => setControllerName(e.target.value)}
                    size="small"
                    required
                    sx={{ flexGrow: 1 }}
                  />
                  <Button type="submit" variant="outlined">
                    Add
                  </Button>
                </Stack>
              </form>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardHeader title="Flow meters" />
          <CardContent>
            <Stack spacing={2}>
              <TableContainer sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableBody>
                    {(meters.data ?? []).map((meter) => (
                      <TableRow key={meter.id} hover>
                        <TableCell>Meter #{meter.id}</TableCell>
                        <TableCell>port {meter.port_name}</TableCell>
                        <TableCell>{meter.ticks_per_ml} ticks/mL</TableCell>
                        <TableCell>
                          {meter.tap_id != null ? `tap #${meter.tap_id}` : "unattached"}
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="error"
                            onClick={() =>
                              void act(
                                () => unwrap(flowMetersDestroy({ path: { id: meter.id } })),
                                "Meter deleted.",
                              )
                            }
                          >
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void act(
                    () =>
                      unwrap(
                        flowMetersCreate({
                          body: {
                            controller_id: Number(meterForm.controllerId),
                            port_name: meterForm.port,
                            ticks_per_ml: Number(meterForm.ticksPerMl) || undefined,
                          } as never,
                        }),
                      ),
                    "Meter created.",
                  );
                }}
              >
                <Stack direction="row" spacing={2} sx={{ flexWrap: "wrap", alignItems: "center" }}>
                  <TextField
                    select
                    label="Controller"
                    value={meterForm.controllerId}
                    onChange={(e) => setMeterForm({ ...meterForm, controllerId: e.target.value })}
                    size="small"
                    sx={{ minWidth: 160 }}
                    slotProps={{ select: { native: true } }}
                  >
                    <option value="" />
                    {(controllers.data ?? []).map((controller) => (
                      <option key={controller.id} value={String(controller.id)}>
                        {controller.name}
                      </option>
                    ))}
                  </TextField>
                  <TextField
                    label="Port name"
                    value={meterForm.port}
                    onChange={(e) => setMeterForm({ ...meterForm, port: e.target.value })}
                    size="small"
                    required
                  />
                  <TextField
                    label="Ticks per mL"
                    type="number"
                    value={meterForm.ticksPerMl}
                    onChange={(e) => setMeterForm({ ...meterForm, ticksPerMl: e.target.value })}
                    size="small"
                  />
                  <Button type="submit" variant="outlined" disabled={!meterForm.controllerId}>
                    Add meter
                  </Button>
                </Stack>
              </form>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardHeader title="Flow toggles" subheader="Relays/valves controlling each tap." />
          <CardContent>
            <Stack spacing={2}>
              <TableContainer sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableBody>
                    {(toggles.data ?? []).map((toggle) => (
                      <TableRow key={toggle.id} hover>
                        <TableCell>Toggle #{toggle.id}</TableCell>
                        <TableCell>port {toggle.port_name}</TableCell>
                        <TableCell>
                          {toggle.tap_id != null ? `tap #${toggle.tap_id}` : "unattached"}
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="error"
                            onClick={() =>
                              void act(
                                () => unwrap(flowTogglesDestroy({ path: { id: toggle.id } })),
                                "Toggle deleted.",
                              )
                            }
                          >
                            Delete
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void act(
                    () =>
                      unwrap(
                        flowTogglesCreate({
                          body: {
                            controller_id: Number(toggleForm.controllerId),
                            port_name: toggleForm.port,
                          } as never,
                        }),
                      ),
                    "Toggle created.",
                  );
                }}
              >
                <Stack direction="row" spacing={2} sx={{ flexWrap: "wrap", alignItems: "center" }}>
                  <TextField
                    select
                    label="Controller"
                    value={toggleForm.controllerId}
                    onChange={(e) => setToggleForm({ ...toggleForm, controllerId: e.target.value })}
                    size="small"
                    sx={{ minWidth: 160 }}
                    slotProps={{ select: { native: true } }}
                  >
                    <option value="" />
                    {(controllers.data ?? []).map((controller) => (
                      <option key={controller.id} value={String(controller.id)}>
                        {controller.name}
                      </option>
                    ))}
                  </TextField>
                  <TextField
                    label="Port name"
                    value={toggleForm.port}
                    onChange={(e) => setToggleForm({ ...toggleForm, port: e.target.value })}
                    size="small"
                    required
                  />
                  <Button type="submit" variant="outlined" disabled={!toggleForm.controllerId}>
                    Add toggle
                  </Button>
                </Stack>
              </form>
              <Typography variant="caption" color="text.secondary">
                Attach meters, toggles, and sensors to taps from each tap's page.
              </Typography>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Page>
  );
}
