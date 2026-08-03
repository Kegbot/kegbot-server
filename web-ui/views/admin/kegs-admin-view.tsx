import Button from "@mui/material/Button";
import MuiLink from "@mui/material/Link";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { type FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router";
import type { Keg } from "@/api-client";
import {
  kegsCreate,
  kegsDestroy,
  kegsEndCreate,
  kegsList,
  kegsPartialUpdate,
  kegsReactivateCreate,
  kegsSpillCreate,
} from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { usePrompt } from "@/components/prompt-context";
import { useSnackbar } from "@/components/snackbar-context";
import { useFormatters } from "@/components/use-formatters";
import { toErrorMessage, unwrap } from "@/lib/api";
import SHARED from "@/lib/shared-constants";
import { useCursorList } from "@/lib/use-cursor-list";
import { kegStatusChip } from "@/views/kegs/keg-list-view";

function KegActions({ keg, onChanged }: { keg: Keg; onChanged: () => void }) {
  const confirm = useConfirm();
  const prompt = usePrompt();
  const { showMessage } = useSnackbar();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);

  const act = async (action: () => Promise<unknown>, message: string) => {
    setAnchor(null);
    try {
      await action();
      showMessage(message);
      onChanged();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <>
      <Button size="small" onClick={(e) => setAnchor(e.currentTarget)}>
        Actions
      </Button>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}>
        {keg.status === "available" && (
          <MenuItem
            onClick={() =>
              void act(() => unwrap(kegsEndCreate({ path: { id: keg.id } })), "Keg finished.")
            }
          >
            Mark finished
          </MenuItem>
        )}
        {keg.status === "finished" && (
          <MenuItem
            onClick={() =>
              void act(
                () => unwrap(kegsReactivateCreate({ path: { id: keg.id } })),
                "Keg reactivated.",
              )
            }
          >
            Reactivate
          </MenuItem>
        )}
        <MenuItem
          onClick={async () => {
            setAnchor(null);
            const volume = await prompt({
              title: `Record spill against keg #${keg.id}`,
              label: "Volume (mL)",
              type: "number",
              confirmText: "Record spill",
            });
            if (!volume) {
              return;
            }
            await act(
              () =>
                unwrap(
                  kegsSpillCreate({ path: { id: keg.id }, body: { volume_ml: Number(volume) } }),
                ),
              "Spill recorded.",
            );
          }}
        >
          Record spill…
        </MenuItem>
        <MenuItem
          onClick={async () => {
            setAnchor(null);
            if (
              await confirm({
                title: `Delete keg #${keg.id}?`,
                message: "The keg and ALL of its drinks will be permanently destroyed.",
                confirmText: "Delete keg",
                destructive: true,
              })
            ) {
              await act(() => unwrap(kegsDestroy({ path: { id: keg.id } })), "Keg deleted.");
            }
          }}
        >
          Delete…
        </MenuItem>
      </Menu>
    </>
  );
}

function EditableNotes({ keg, onChanged }: { keg: Keg; onChanged: () => void }) {
  const { showMessage } = useSnackbar();
  const prompt = usePrompt();
  return (
    <MuiLink
      component="button"
      type="button"
      onClick={async () => {
        const description = await prompt({
          title: `Keg #${keg.id} description`,
          label: "Description",
          initialValue: keg.description ?? "",
        });
        if (description === null) {
          return;
        }
        try {
          await unwrap(kegsPartialUpdate({ path: { id: keg.id }, body: { description } }));
          showMessage("Keg updated.");
          onChanged();
        } catch (error) {
          showMessage(toErrorMessage(error), "error");
        }
      }}
    >
      edit
    </MuiLink>
  );
}

const STATUS_TABS = [
  { label: "All", value: "" },
  { label: "On tap", value: "on_tap" },
  { label: "Available", value: "available" },
  { label: "Finished", value: "finished" },
];

export function KegsAdminView() {
  const { volume } = useFormatters();
  const { showMessage } = useSnackbar();
  const [params, setParams] = useSearchParams();
  const status = params.get("status") ?? "";

  const kegs = useCursorList(
    (cursor) => unwrap(kegsList({ query: { cursor, status: (status || undefined) as never } })),
    [status],
  );

  const [beverage, setBeverage] = useState({ name: "", producer: "", style: "" });
  const [kegType, setKegType] = useState("half-barrel");
  const [busy, setBusy] = useState(false);

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    try {
      await unwrap(
        kegsCreate({
          body: {
            beverage_name: beverage.name,
            producer_name: beverage.producer,
            style_name: beverage.style,
            keg_type: kegType as never,
          },
        }),
      );
      showMessage("Keg added to the keg room.");
      setBeverage({ name: "", producer: "", style: "" });
      kegs.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="Keg Room" loading={kegs.loading} error={kegs.error}>
      <Stack spacing={2}>
        <Tabs
          value={status}
          onChange={(_, value) => setParams(value ? { status: value } : {})}
          variant="scrollable"
        >
          {STATUS_TABS.map((tab) => (
            <Tab key={tab.value} label={tab.label} value={tab.value} />
          ))}
        </Tabs>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Keg</TableCell>
                <TableCell>Beverage</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Served</TableCell>
                <TableCell>Description</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {kegs.items.map((keg) => (
                <TableRow key={keg.id} hover>
                  <TableCell>
                    <MuiLink component={Link} to={`/kegs/${keg.id}`} underline="hover">
                      #{keg.id}
                    </MuiLink>
                  </TableCell>
                  <TableCell>{keg.beverage.name}</TableCell>
                  <TableCell>{kegStatusChip(keg)}</TableCell>
                  <TableCell align="right">{volume(keg.served_volume_ml)}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {keg.description || "—"}
                      </Typography>
                      <EditableNotes keg={keg} onChanged={kegs.reload} />
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    <KegActions keg={keg} onChanged={kegs.reload} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={kegs} />
        <Typography variant="h6">Add a keg</Typography>
        <form onSubmit={onCreate}>
          <Stack direction="row" spacing={2} sx={{ flexWrap: "wrap", alignItems: "center" }}>
            <TextField
              label="Beverage"
              value={beverage.name}
              onChange={(e) => setBeverage({ ...beverage, name: e.target.value })}
              size="small"
              required
            />
            <TextField
              label="Producer"
              value={beverage.producer}
              onChange={(e) => setBeverage({ ...beverage, producer: e.target.value })}
              size="small"
              required
            />
            <TextField
              label="Style"
              value={beverage.style}
              onChange={(e) => setBeverage({ ...beverage, style: e.target.value })}
              size="small"
              required
            />
            <TextField
              select
              label="Keg size"
              value={kegType}
              onChange={(e) => setKegType(e.target.value)}
              size="small"
              sx={{ minWidth: 200 }}
            >
              {Object.entries(SHARED.KEG_TYPES).map(([value, label]) => (
                <MenuItem key={value} value={value}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
            <Button type="submit" variant="contained" disabled={busy}>
              Add keg
            </Button>
          </Stack>
        </form>
      </Stack>
    </Page>
  );
}
