import SignalWifi0BarIcon from "@mui/icons-material/SignalWifi0Bar";
import SignalWifi1BarIcon from "@mui/icons-material/SignalWifi1Bar";
import SignalWifi2BarIcon from "@mui/icons-material/SignalWifi2Bar";
import SignalWifi3BarIcon from "@mui/icons-material/SignalWifi3Bar";
import SignalWifi4BarIcon from "@mui/icons-material/SignalWifi4Bar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Collapse from "@mui/material/Collapse";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, Fragment, type ReactNode, useState } from "react";
import type { Controller, FlowMeter, FlowToggle, KegboardDevice, KegTap } from "@/api-client";
import {
  adminKegboardsAllowCreate,
  adminKegboardsDenyCreate,
  adminKegboardsDestroy,
  adminKegboardsList,
  controllersCreate,
  controllersDestroy,
  controllersList,
  flowMetersCreate,
  flowMetersDestroy,
  flowMetersList,
  flowTogglesCreate,
  flowTogglesDestroy,
  flowTogglesList,
  tapsConnectMeterCreate,
  tapsConnectToggleCreate,
  tapsList,
} from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { useSnackbar } from "@/components/snackbar-context";
import { useFormatters } from "@/components/use-formatters";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { MONO_FONT } from "@/theme/typography";

type Act = (action: () => Promise<unknown>, message: string) => Promise<void>;

const DEFAULT_HEARTBEAT_MS = 60_000;

function isOnline(device: KegboardDevice): boolean {
  if (!device.last_seen) {
    return false;
  }
  const heartbeat = Number(device.config?.heartbeat_ms) || DEFAULT_HEARTBEAT_MS;
  return Date.now() - new Date(device.last_seen).getTime() < heartbeat * 2.5;
}

const WIFI_ICONS = [
  SignalWifi0BarIcon,
  SignalWifi1BarIcon,
  SignalWifi2BarIcon,
  SignalWifi3BarIcon,
  SignalWifi4BarIcon,
];

/** Signal-bar icon plus the raw dBm reading. */
function WifiStrength({ rssiDbm }: { rssiDbm: number }) {
  // Typical Wi-Fi quality thresholds.
  const bars =
    rssiDbm >= -50 ? 4 : rssiDbm >= -60 ? 3 : rssiDbm >= -70 ? 2 : rssiDbm >= -80 ? 1 : 0;
  const Icon = WIFI_ICONS[bars];
  const color = bars >= 3 ? "success.main" : bars === 2 ? "warning.main" : "error.main";
  return (
    <Stack
      direction="row"
      spacing={0.75}
      sx={{ alignItems: "center", justifyContent: "flex-end", display: "inline-flex" }}
    >
      <Icon fontSize="small" sx={{ color }} />
      <Box component="span" sx={{ fontFamily: MONO_FONT }}>
        {rssiDbm} dBm
      </Box>
    </Stack>
  );
}

function OnlineDot({ online }: { online: boolean }) {
  return (
    <Box
      component="span"
      sx={{
        display: "inline-block",
        width: 8,
        height: 8,
        borderRadius: "50%",
        bgcolor: online ? "success.main" : "text.disabled",
        mr: 1,
      }}
    />
  );
}

/** Inline tap picker for a meter or toggle row. */
function TapSelect({
  taps,
  value,
  onChange,
}: {
  taps: KegTap[];
  value: number | null | undefined;
  onChange: (tapId: number | null) => void;
}) {
  return (
    <TextField
      select
      size="small"
      label="Tap"
      value={value != null ? String(value) : ""}
      onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
      sx={{ minWidth: 180 }}
    >
      <MenuItem value="">
        <em>Unassigned</em>
      </MenuItem>
      {taps.map((tap) => (
        <MenuItem key={tap.id} value={String(tap.id)}>
          {tap.name}
        </MenuItem>
      ))}
    </TextField>
  );
}

function PortRow({
  port,
  detail,
  children,
  onDelete,
}: {
  port: string;
  detail?: string;
  children: ReactNode;
  onDelete?: () => void;
}) {
  return (
    <Stack direction="row" spacing={2} sx={{ alignItems: "center", flexWrap: "wrap" }}>
      <Box sx={{ fontFamily: MONO_FONT, fontWeight: 600, minWidth: 88 }}>{port}</Box>
      <Typography variant="body2" color="text.secondary" sx={{ minWidth: 110 }}>
        {detail ?? ""}
      </Typography>
      {children}
      {onDelete && (
        <Button size="small" color="error" onClick={onDelete}>
          Delete
        </Button>
      )}
    </Stack>
  );
}

/**
 * Meters and toggles for one controller, with inline tap assignment.
 *
 * `managed` controllers (kegboards) own their port inventory and
 * calibration device-side: ports can't be added, deleted, or
 * recalibrated here — only assigned to taps.
 */
function ControllerConfig({
  controller,
  meters,
  toggles,
  taps,
  act,
  managed,
  footer,
}: {
  controller: Controller;
  meters: FlowMeter[];
  toggles: FlowToggle[];
  taps: KegTap[];
  act: Act;
  managed?: boolean;
  footer?: ReactNode;
}) {
  const [meterForm, setMeterForm] = useState({ port: "", ticksPerMl: "" });
  const [togglePort, setTogglePort] = useState("");

  const assignMeter = (meter: FlowMeter, tapId: number | null) =>
    act(async () => {
      if (tapId != null) {
        await unwrap(tapsConnectMeterCreate({ path: { id: tapId }, body: { meter_id: meter.id } }));
      } else if (meter.tap_id != null) {
        await unwrap(
          tapsConnectMeterCreate({ path: { id: meter.tap_id }, body: { meter_id: null } }),
        );
      }
    }, "Meter assignment saved.");

  const assignToggle = (toggle: FlowToggle, tapId: number | null) =>
    act(async () => {
      if (tapId != null) {
        await unwrap(
          tapsConnectToggleCreate({ path: { id: tapId }, body: { toggle_id: toggle.id } }),
        );
      } else if (toggle.tap_id != null) {
        await unwrap(
          tapsConnectToggleCreate({ path: { id: toggle.tap_id }, body: { toggle_id: null } }),
        );
      }
    }, "Relay assignment saved.");

  return (
    <Stack spacing={3} sx={{ py: 2 }}>
      <Stack spacing={1.5}>
        <Typography variant="overline" color="text.secondary" component="div">
          Meters
        </Typography>
        {meters.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No meters.
          </Typography>
        )}
        {meters.map((meter) => (
          <PortRow
            key={meter.id}
            port={meter.port_name}
            detail={`${meter.ticks_per_ml} ticks/mL`}
            onDelete={
              managed
                ? undefined
                : () =>
                    void act(
                      () => unwrap(flowMetersDestroy({ path: { id: meter.id } })),
                      "Meter deleted.",
                    )
            }
          >
            <TapSelect
              taps={taps}
              value={meter.tap_id}
              onChange={(tapId) => void assignMeter(meter, tapId)}
            />
          </PortRow>
        ))}
        {!managed && (
          <form
            onSubmit={(e: FormEvent) => {
              e.preventDefault();
              void act(
                () =>
                  unwrap(
                    flowMetersCreate({
                      body: {
                        controller_id: controller.id,
                        port_name: meterForm.port,
                        ticks_per_ml: Number(meterForm.ticksPerMl) || undefined,
                      } as never,
                    }),
                  ),
                "Meter created.",
              ).then(() => setMeterForm({ port: "", ticksPerMl: "" }));
            }}
          >
            <Stack direction="row" spacing={1.5} sx={{ alignItems: "center", flexWrap: "wrap" }}>
              <TextField
                label="New meter port"
                value={meterForm.port}
                onChange={(e) => setMeterForm({ ...meterForm, port: e.target.value })}
                size="small"
                placeholder="flow0"
                required
              />
              <TextField
                label="Ticks per mL"
                type="number"
                value={meterForm.ticksPerMl}
                onChange={(e) => setMeterForm({ ...meterForm, ticksPerMl: e.target.value })}
                size="small"
                sx={{ width: 130 }}
              />
              <Button type="submit" size="small" variant="outlined">
                Add meter
              </Button>
            </Stack>
          </form>
        )}
      </Stack>

      <Stack spacing={1.5}>
        <Typography variant="overline" color="text.secondary" component="div">
          Relays
        </Typography>
        {toggles.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            No relays.
          </Typography>
        )}
        {toggles.map((toggle) => (
          <PortRow
            key={toggle.id}
            port={toggle.port_name}
            onDelete={
              managed
                ? undefined
                : () =>
                    void act(
                      () => unwrap(flowTogglesDestroy({ path: { id: toggle.id } })),
                      "Relay deleted.",
                    )
            }
          >
            <TapSelect
              taps={taps}
              value={toggle.tap_id}
              onChange={(tapId) => void assignToggle(toggle, tapId)}
            />
          </PortRow>
        ))}
        {!managed && (
          <form
            onSubmit={(e: FormEvent) => {
              e.preventDefault();
              void act(
                () =>
                  unwrap(
                    flowTogglesCreate({
                      body: {
                        controller_id: controller.id,
                        port_name: togglePort,
                      } as never,
                    }),
                  ),
                "Relay created.",
              ).then(() => setTogglePort(""));
            }}
          >
            <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
              <TextField
                label="New relay port"
                value={togglePort}
                onChange={(e) => setTogglePort(e.target.value)}
                size="small"
                placeholder="relay0"
                required
              />
              <Button type="submit" size="small" variant="outlined">
                Add relay
              </Button>
            </Stack>
          </form>
        )}
      </Stack>

      {managed && (
        <Typography variant="caption" color="text.secondary">
          Ports and calibration are managed by the board.
        </Typography>
      )}

      {footer}
    </Stack>
  );
}

/** A clickable row plus its collapsible detail row. */
function ExpandableRow({
  cells,
  colSpan,
  expanded,
  onToggle,
  children,
}: {
  cells: ReactNode;
  colSpan: number;
  expanded: boolean;
  onToggle: () => void;
  children: ReactNode;
}) {
  return (
    <Fragment>
      <TableRow
        hover
        onClick={onToggle}
        sx={{ cursor: "pointer", "& > td": expanded ? { borderBottom: "none" } : undefined }}
      >
        {cells}
      </TableRow>
      <TableRow>
        <TableCell colSpan={colSpan} sx={{ py: 0, border: expanded ? undefined : "none" }}>
          <Collapse in={expanded} unmountOnExit>
            {children}
          </Collapse>
        </TableCell>
      </TableRow>
    </Fragment>
  );
}

export function ControllersView() {
  const { showMessage } = useSnackbar();
  const { relative } = useFormatters();
  const confirm = useConfirm();

  const kegboards = useAsyncData(async () => unwrap(adminKegboardsList()), { pollMs: 5000 });
  const controllers = useAsyncData(
    async () => (await unwrap(controllersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const meters = useAsyncData(
    async () => (await unwrap(flowMetersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const toggles = useAsyncData(
    async () => (await unwrap(flowTogglesList({ query: { page_size: 100 } }))).results ?? [],
  );
  const taps = useAsyncData(
    async () => (await unwrap(tapsList({ query: { page_size: 100 } }))).results ?? [],
  );

  const [expanded, setExpanded] = useState<string | null>(null);
  const [controllerName, setControllerName] = useState("");

  const reloadAll = () => {
    kegboards.reload();
    controllers.reload();
    meters.reload();
    toggles.reload();
    taps.reload();
  };

  const act: Act = async (action, message) => {
    try {
      await action();
      showMessage(message);
      reloadAll();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  const toggleExpanded = (key: string) => setExpanded((current) => (current === key ? null : key));

  const configFor = (controller: Controller, managed: boolean, footer?: ReactNode) => (
    <ControllerConfig
      controller={controller}
      meters={(meters.data ?? []).filter((m) => m.controller_id === controller.id)}
      toggles={(toggles.data ?? []).filter((t) => t.controller_id === controller.id)}
      taps={taps.data ?? []}
      act={act}
      managed={managed}
      footer={footer}
    />
  );

  // Kegboard actions.

  const allow = (device: KegboardDevice) =>
    act(
      () => unwrap(adminKegboardsAllowCreate({ path: { device: device.device } })),
      `${device.device} allowed; it will pair on its next check-in.`,
    );

  const deny = (device: KegboardDevice) =>
    act(
      () => unwrap(adminKegboardsDenyCreate({ path: { device: device.device } })),
      `${device.device} denied.`,
    );

  const forget = (device: KegboardDevice) =>
    act(
      () => unwrap(adminKegboardsDestroy({ path: { device: device.device } })),
      `${device.device} removed.`,
    );

  const removeController = async (controller: Controller, isKegboard: boolean) => {
    if (
      await confirm({
        title: `Delete controller "${controller.name}"?`,
        message: isKegboard
          ? "Its meters and toggles are deleted with it, and the board's access is revoked. Drinks are kept; the board will reappear here for pairing."
          : "Its meters and toggles are deleted with it. Drinks are kept.",
        confirmText: "Delete",
        destructive: true,
      })
    ) {
      await act(
        () => unwrap(controllersDestroy({ path: { id: controller.id } })),
        "Controller deleted.",
      );
    }
  };

  const allKegboards = kegboards.data ?? [];
  const kegboardControllerIds = new Set(
    allKegboards.map((d) => d.controller_id).filter((id) => id != null),
  );
  const controllerById = new Map((controllers.data ?? []).map((c) => [c.id, c]));
  const otherControllers = (controllers.data ?? []).filter((c) => !kegboardControllerIds.has(c.id));

  const stateChip = (device: KegboardDevice) => {
    // A rejected batch trumps the pairing state: the board is talking,
    // but the server can't understand it.
    const errorChip = device.last_error ? (
      <Chip
        label="rejected requests"
        color="error"
        size="small"
        variant="outlined"
        title={device.last_error}
      />
    ) : null;
    if (device.state === "paired") {
      return errorChip ?? (device.last_seen ? relative(device.last_seen) : "—");
    }
    const label =
      device.state === "pending"
        ? "wants to pair"
        : device.state === "allowed"
          ? "pairing…"
          : "denied";
    const color = device.state === "pending" ? "warning" : "default";
    return (
      <Stack direction="row" spacing={1} sx={{ display: "inline-flex" }}>
        <Chip label={label} color={color} size="small" variant="outlined" />
        {errorChip}
      </Stack>
    );
  };

  return (
    <Page
      title="Controllers"
      loading={controllers.loading || meters.loading || toggles.loading || taps.loading}
      error={controllers.error ?? meters.error ?? toggles.error ?? taps.error}
    >
      <Stack spacing={4}>
        <Section label="Kegboards">
          <Stack spacing={2}>
            <Typography variant="body2" color="text.secondary">
              Kegboards on your network announce themselves here automatically; approve a board to
              start recording its pours.
            </Typography>
            {allKegboards.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No kegboards have announced themselves yet. A board configured with this server's
                address appears here automatically.
              </Typography>
            ) : (
              <TableContainer sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Board</TableCell>
                      <TableCell>Last seen</TableCell>
                      <TableCell>Firmware</TableCell>
                      <TableCell align="right">Wi-Fi</TableCell>
                      <TableCell align="right">Dropped</TableCell>
                      <TableCell align="right" />
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {allKegboards.map((device) => {
                      const controller =
                        device.controller_id != null
                          ? controllerById.get(device.controller_id)
                          : undefined;
                      const cells = (
                        <Fragment>
                          <TableCell sx={{ fontFamily: MONO_FONT }}>
                            <OnlineDot online={isOnline(device)} />
                            {device.device}
                          </TableCell>
                          <TableCell sx={{ color: "text.secondary" }}>
                            {stateChip(device)}
                          </TableCell>
                          <TableCell sx={{ color: "text.secondary" }}>
                            {device.fw_version ?? "—"}
                          </TableCell>
                          <TableCell align="right">
                            {device.wifi_rssi_dbm != null ? (
                              <WifiStrength rssiDbm={device.wifi_rssi_dbm} />
                            ) : (
                              "—"
                            )}
                          </TableCell>
                          <TableCell align="right" sx={{ fontFamily: MONO_FONT }}>
                            {(device.events_dropped ?? 0) > 0 ? (
                              <Chip
                                label={device.events_dropped}
                                color="warning"
                                size="small"
                                variant="outlined"
                              />
                            ) : (
                              "0"
                            )}
                          </TableCell>
                          <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                            {(device.state === "pending" || device.state === "denied") && (
                              <Stack
                                direction="row"
                                spacing={1}
                                sx={{ justifyContent: "flex-end" }}
                              >
                                <Button
                                  size="small"
                                  variant="contained"
                                  onClick={() => void allow(device)}
                                >
                                  Allow
                                </Button>
                                {device.state === "denied" ? (
                                  <Button size="small" onClick={() => void forget(device)}>
                                    Forget
                                  </Button>
                                ) : (
                                  <Button
                                    size="small"
                                    color="error"
                                    onClick={() => void deny(device)}
                                  >
                                    Deny
                                  </Button>
                                )}
                              </Stack>
                            )}
                          </TableCell>
                        </Fragment>
                      );
                      if (!controller) {
                        return (
                          <TableRow key={device.device} hover>
                            {cells.props.children}
                          </TableRow>
                        );
                      }
                      return (
                        <ExpandableRow
                          key={device.device}
                          cells={cells}
                          colSpan={6}
                          expanded={expanded === device.device}
                          onToggle={() => toggleExpanded(device.device)}
                        >
                          {configFor(
                            controller,
                            true,
                            <Box>
                              <Button
                                size="small"
                                variant="outlined"
                                color="error"
                                onClick={() => void removeController(controller, true)}
                              >
                                Delete controller
                              </Button>
                            </Box>,
                          )}
                        </ExpandableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Stack>
        </Section>

        <Section label="Other controllers">
          <Stack spacing={2}>
            <Typography variant="body2" color="text.secondary">
              Manually configured (legacy) controllers, e.g. kegbot-pycore.
            </Typography>
            {otherControllers.length > 0 && (
              <TableContainer sx={{ overflowX: "auto" }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Model</TableCell>
                      <TableCell>Serial</TableCell>
                      <TableCell>Ports</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {otherControllers.map((controller) => {
                      const meterCount = (meters.data ?? []).filter(
                        (m) => m.controller_id === controller.id,
                      ).length;
                      const toggleCount = (toggles.data ?? []).filter(
                        (t) => t.controller_id === controller.id,
                      ).length;
                      return (
                        <ExpandableRow
                          key={controller.id}
                          colSpan={4}
                          expanded={expanded === `c${controller.id}`}
                          onToggle={() => toggleExpanded(`c${controller.id}`)}
                          cells={
                            <Fragment>
                              <TableCell sx={{ fontFamily: MONO_FONT }}>
                                {controller.name}
                              </TableCell>
                              <TableCell sx={{ color: "text.secondary" }}>
                                {controller.model_name ?? "—"}
                              </TableCell>
                              <TableCell sx={{ color: "text.secondary" }}>
                                {controller.serial_number ?? "—"}
                              </TableCell>
                              <TableCell sx={{ color: "text.secondary" }}>
                                {meterCount} {meterCount === 1 ? "meter" : "meters"} · {toggleCount}{" "}
                                {toggleCount === 1 ? "relay" : "relays"}
                              </TableCell>
                            </Fragment>
                          }
                        >
                          {configFor(
                            controller,
                            false,
                            <Box>
                              <Button
                                size="small"
                                variant="outlined"
                                color="error"
                                onClick={() => void removeController(controller, false)}
                              >
                                Delete controller
                              </Button>
                            </Box>,
                          )}
                        </ExpandableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
            <form onSubmit={(e) => e.preventDefault()}>
              <Stack direction="row" spacing={2} sx={{ alignItems: "center", maxWidth: 480 }}>
                <TextField
                  label="New controller name"
                  value={controllerName}
                  onChange={(e) => setControllerName(e.target.value)}
                  size="small"
                  required
                  sx={{ flexGrow: 1 }}
                />
                <Button
                  type="submit"
                  variant="outlined"
                  onClick={() =>
                    void act(
                      () => unwrap(controllersCreate({ body: { name: controllerName } })),
                      "Controller created.",
                    ).then(() => setControllerName(""))
                  }
                >
                  Add controller
                </Button>
              </Stack>
            </form>
          </Stack>
        </Section>
      </Stack>
    </Page>
  );
}
