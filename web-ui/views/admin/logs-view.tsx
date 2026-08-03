import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { adminLogsRetrieve } from "@/api";
import { Page } from "@/components/page";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

interface LogsPayload {
  logs: unknown[];
  error: string | null;
}

function formatRecord(record: unknown): string {
  if (typeof record === "string") {
    try {
      const parsed = JSON.parse(record) as Record<string, unknown>;
      return `${parsed.time ?? ""} ${parsed.name ?? ""} ${parsed.msg ?? record}`;
    } catch {
      return record;
    }
  }
  return JSON.stringify(record);
}

export function LogsView() {
  const logs = useAsyncData(
    async () => (await unwrap(adminLogsRetrieve())) as unknown as LogsPayload,
  );

  return (
    <Page title="Logs" loading={logs.loading} error={logs.error}>
      {logs.data?.error && <Alert severity="warning">{logs.data.error}</Alert>}
      {logs.data && logs.data.logs.length === 0 && !logs.data.error && (
        <Typography color="text.secondary">No recent log records.</Typography>
      )}
      {logs.data && logs.data.logs.length > 0 && (
        <Box
          component="pre"
          sx={{
            fontFamily: "monospace",
            fontSize: 13,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            bgcolor: "action.hover",
            p: 2,
            borderRadius: 1,
            overflowX: "auto",
          }}
        >
          {logs.data.logs.map((record) => formatRecord(record)).join("\n")}
        </Box>
      )}
    </Page>
  );
}
