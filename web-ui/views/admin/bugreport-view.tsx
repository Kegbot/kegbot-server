import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { adminBugreportRetrieve } from "@/api";
import { Page } from "@/components/page";
import { toErrorMessage, unwrap } from "@/lib/api";

interface BugreportPayload {
  output: string;
  error: string | null;
}

export function BugreportView() {
  const [busy, setBusy] = useState(false);
  const [report, setReport] = useState<BugreportPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      setReport((await unwrap(adminBugreportRetrieve())) as unknown as BugreportPayload);
    } catch (e) {
      setError(toErrorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Page title="Bug Report">
      <Stack spacing={2}>
        <Typography color="text.secondary">
          Generates a diagnostic report (versions, environment, recent logs). It may contain secrets
          — share with care.
        </Typography>
        <Button
          onClick={() => void generate()}
          variant="contained"
          disabled={busy}
          sx={{ alignSelf: "flex-start" }}
        >
          {busy ? "Generating…" : "Generate bugreport"}
        </Button>
        {error && <Alert severity="error">{error}</Alert>}
        {report?.error && <Alert severity="warning">{report.error}</Alert>}
        {report && (
          <Box
            component="pre"
            sx={{
              fontFamily: "monospace",
              fontSize: 12,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              bgcolor: "action.hover",
              p: 2,
              borderRadius: 1,
              overflowX: "auto",
              maxHeight: 600,
              overflowY: "auto",
            }}
          >
            {report.output}
          </Box>
        )}
      </Stack>
    </Page>
  );
}
