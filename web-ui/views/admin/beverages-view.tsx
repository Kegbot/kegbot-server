import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import { useState } from "react";
import type { Beverage } from "@/api";
import {
  beverageProducersList,
  beveragesCreate,
  beveragesList,
  beveragesPartialUpdate,
  beveragesPictureCreate,
} from "@/api";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import SHARED from "@/lib/shared-constants";
import { useAsyncData } from "@/lib/use-async-data";
import { useCursorList } from "@/lib/use-cursor-list";

interface EditorState {
  beverage: Beverage | null;
  name: string;
  producerId: string;
  style: string;
  beverageType: string;
  abv: string;
}

const CLOSED: EditorState | null = null;

export function BeveragesView() {
  const { showMessage } = useSnackbar();
  const beverages = useCursorList((cursor) => unwrap(beveragesList({ query: { cursor } })));
  const producers = useAsyncData(
    async () => (await unwrap(beverageProducersList({ query: { page_size: 100 } }))).results ?? [],
  );
  const [editor, setEditor] = useState<EditorState | null>(CLOSED);
  const [busy, setBusy] = useState(false);

  const openCreate = () =>
    setEditor({
      beverage: null,
      name: "",
      producerId: "",
      style: "",
      beverageType: "beer",
      abv: "",
    });

  const openEdit = (beverage: Beverage) =>
    setEditor({
      beverage,
      name: beverage.name,
      producerId: String(beverage.producer.id),
      style: beverage.style ?? "",
      beverageType: beverage.beverage_type ?? "beer",
      abv: beverage.abv_percent != null ? String(beverage.abv_percent) : "",
    });

  const saveEditor = async () => {
    if (!editor) {
      return;
    }
    setBusy(true);
    const body = {
      name: editor.name,
      producer_id: Number(editor.producerId),
      style: editor.style,
      beverage_type: editor.beverageType as never,
      abv_percent: editor.abv === "" ? null : Number(editor.abv),
    };
    try {
      if (editor.beverage) {
        await unwrap(beveragesPartialUpdate({ path: { id: editor.beverage.id }, body }));
        showMessage("Beverage updated.");
      } else {
        await unwrap(beveragesCreate({ body }));
        showMessage("Beverage created.");
      }
      setEditor(CLOSED);
      beverages.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  const uploadPicture = async (beverage: Beverage, file: File | undefined) => {
    if (!file) {
      return;
    }
    try {
      await unwrap(beveragesPictureCreate({ path: { id: beverage.id }, body: { image: file } }));
      showMessage("Picture updated.");
      beverages.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page
      title="Beverages"
      loading={beverages.loading}
      error={beverages.error}
      headerRight={
        <Button variant="contained" onClick={openCreate}>
          Add beverage
        </Button>
      }
    >
      <Stack spacing={2}>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Producer</TableCell>
                <TableCell>Style</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="right">ABV %</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {beverages.items.map((beverage) => (
                <TableRow key={beverage.id} hover>
                  <TableCell>{beverage.name}</TableCell>
                  <TableCell>{beverage.producer.name}</TableCell>
                  <TableCell>{beverage.style}</TableCell>
                  <TableCell>{beverage.beverage_type}</TableCell>
                  <TableCell align="right">{beverage.abv_percent ?? "—"}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} sx={{ justifyContent: "flex-end" }}>
                      <Button size="small" onClick={() => openEdit(beverage)}>
                        Edit
                      </Button>
                      <Button size="small" component="label">
                        Picture
                        <input
                          hidden
                          type="file"
                          accept="image/*"
                          onChange={(e) => void uploadPicture(beverage, e.target.files?.[0])}
                        />
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={beverages} />
      </Stack>

      <Dialog open={editor !== null} onClose={() => setEditor(CLOSED)} fullWidth maxWidth="sm">
        <DialogTitle>{editor?.beverage ? "Edit beverage" : "Add beverage"}</DialogTitle>
        <DialogContent>
          {editor && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                label="Name"
                value={editor.name}
                onChange={(e) => setEditor({ ...editor, name: e.target.value })}
                required
              />
              <TextField
                select
                label="Producer"
                value={editor.producerId}
                onChange={(e) => setEditor({ ...editor, producerId: e.target.value })}
                required
              >
                {(producers.data ?? []).map((producer) => (
                  <MenuItem key={producer.id} value={String(producer.id)}>
                    {producer.name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Style"
                value={editor.style}
                onChange={(e) => setEditor({ ...editor, style: e.target.value })}
              />
              <TextField
                select
                label="Type"
                value={editor.beverageType}
                onChange={(e) => setEditor({ ...editor, beverageType: e.target.value })}
              >
                {Object.entries(SHARED.BEVERAGE_TYPES).map(([value, label]) => (
                  <MenuItem key={value} value={value}>
                    {label}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="ABV %"
                type="number"
                value={editor.abv}
                onChange={(e) => setEditor({ ...editor, abv: e.target.value })}
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditor(CLOSED)}>Cancel</Button>
          <Button onClick={() => void saveEditor()} variant="contained" disabled={busy}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
}
