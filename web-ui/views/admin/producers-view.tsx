import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import { useState } from "react";
import type { BeverageProducer } from "@/api";
import {
  beverageProducersCreate,
  beverageProducersList,
  beverageProducersPartialUpdate,
  beverageProducersPictureCreate,
} from "@/api";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { toErrorMessage, unwrap } from "@/lib/api";
import { useCursorList } from "@/lib/use-cursor-list";

interface EditorState {
  producer: BeverageProducer | null;
  name: string;
  country: string;
  url: string;
  isHomebrew: boolean;
}

export function ProducersView() {
  const { showMessage } = useSnackbar();
  const producers = useCursorList((cursor) => unwrap(beverageProducersList({ query: { cursor } })));
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    if (!editor) {
      return;
    }
    setBusy(true);
    const body = {
      name: editor.name,
      country: editor.country as never,
      url: editor.url,
      is_homebrew: editor.isHomebrew,
    };
    try {
      if (editor.producer) {
        await unwrap(beverageProducersPartialUpdate({ path: { id: editor.producer.id }, body }));
        showMessage("Producer updated.");
      } else {
        await unwrap(beverageProducersCreate({ body }));
        showMessage("Producer created.");
      }
      setEditor(null);
      producers.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  };

  const uploadPicture = async (producer: BeverageProducer, file: File | undefined) => {
    if (!file) {
      return;
    }
    try {
      await unwrap(
        beverageProducersPictureCreate({ path: { id: producer.id }, body: { image: file } }),
      );
      showMessage("Picture updated.");
      producers.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page
      title="Producers"
      loading={producers.loading}
      error={producers.error}
      headerRight={
        <Button
          variant="contained"
          onClick={() =>
            setEditor({ producer: null, name: "", country: "", url: "", isHomebrew: false })
          }
        >
          Add producer
        </Button>
      }
    >
      <Stack spacing={2}>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Homebrew?</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {producers.items.map((producer) => (
                <TableRow key={producer.id} hover>
                  <TableCell>{producer.name}</TableCell>
                  <TableCell>{producer.country}</TableCell>
                  <TableCell>{producer.is_homebrew ? "Yes" : ""}</TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} sx={{ justifyContent: "flex-end" }}>
                      <Button
                        size="small"
                        onClick={() =>
                          setEditor({
                            producer,
                            name: producer.name,
                            country: producer.country ?? "",
                            url: producer.url ?? "",
                            isHomebrew: producer.is_homebrew ?? false,
                          })
                        }
                      >
                        Edit
                      </Button>
                      <Button size="small" component="label">
                        Picture
                        <input
                          hidden
                          type="file"
                          accept="image/*"
                          onChange={(e) => void uploadPicture(producer, e.target.files?.[0])}
                        />
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={producers} />
      </Stack>

      <Dialog open={editor !== null} onClose={() => setEditor(null)} fullWidth maxWidth="sm">
        <DialogTitle>{editor?.producer ? "Edit producer" : "Add producer"}</DialogTitle>
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
                label="Country"
                value={editor.country}
                onChange={(e) => setEditor({ ...editor, country: e.target.value })}
              />
              <TextField
                label="URL"
                value={editor.url}
                onChange={(e) => setEditor({ ...editor, url: e.target.value })}
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={editor.isHomebrew}
                    onChange={(e) => setEditor({ ...editor, isHomebrew: e.target.checked })}
                  />
                }
                label="Homebrew"
              />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditor(null)}>Cancel</Button>
          <Button onClick={() => void save()} variant="contained" disabled={busy}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Page>
  );
}
