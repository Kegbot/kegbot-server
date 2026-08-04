import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { adminLogsRetrieve } from "@/api-client";
import { Page } from "@/components/page";
import { unwrap } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { useAsyncData } from "@/lib/use-async-data";
import { MONO_FONT } from "@/theme/typography";

interface LogsPayload {
  logs: unknown[];
  error: string | null;
}

/** One parsed record from the redis log handler. */
interface LogRecord {
  time?: string;
  level?: string;
  name?: string;
  message: string;
  traceback?: string | null;
  /** Original text, shown when the record can't be parsed. */
  raw?: string;
}

/** Interpolates python %-style placeholders ("%s", "%d") with args. */
function interpolate(template: string, args: unknown): string {
  if (!Array.isArray(args) || args.length === 0) {
    return template;
  }
  let index = 0;
  return template.replace(/%[sdifr]/g, (token) =>
    index < args.length ? String(args[index++]) : token,
  );
}

function parseRecord(record: unknown): LogRecord {
  let data: Record<string, unknown> | null = null;
  if (typeof record === "string") {
    try {
      const parsed: unknown = JSON.parse(record);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        data = parsed as Record<string, unknown>;
      }
    } catch {
      return { message: record, raw: record };
    }
  } else if (record && typeof record === "object" && !Array.isArray(record)) {
    data = record as Record<string, unknown>;
  }
  if (!data) {
    return { message: String(record), raw: String(record) };
  }
  const template = typeof data.msg === "string" ? data.msg : JSON.stringify(data.msg);
  return {
    time: typeof data.time === "string" ? data.time : undefined,
    level: typeof data.level === "string" ? data.level : undefined,
    name: typeof data.name === "string" ? data.name : undefined,
    message: interpolate(template, data.args),
    traceback: typeof data.traceback === "string" ? data.traceback : null,
  };
}

const LEVEL_COLORS: Record<string, "default" | "info" | "warning" | "error"> = {
  debug: "default",
  info: "info",
  warning: "warning",
  error: "error",
  critical: "error",
};

function LevelChip({ level }: { level?: string }) {
  if (!level) {
    return null;
  }
  return (
    <Chip
      label={level.toUpperCase()}
      color={LEVEL_COLORS[level.toLowerCase()] ?? "default"}
      size="small"
      variant="outlined"
      sx={{ fontFamily: MONO_FONT, fontSize: "0.6875rem" }}
    />
  );
}

export function LogsView() {
  const logs = useAsyncData(
    async () => (await unwrap(adminLogsRetrieve())) as unknown as LogsPayload,
  );
  const records = (logs.data?.logs ?? []).map(parseRecord);

  return (
    <Page title="Logs" loading={logs.loading} error={logs.error}>
      {logs.data?.error && <Alert severity="warning">{logs.data.error}</Alert>}
      {logs.data && records.length === 0 && !logs.data.error && (
        <Typography color="text.secondary">No recent log records.</Typography>
      )}
      {records.length > 0 && (
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Time</TableCell>
                <TableCell>Level</TableCell>
                <TableCell>Logger</TableCell>
                <TableCell>Message</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {records.map((record, index) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: records have no id
                <TableRow key={index} hover sx={{ verticalAlign: "top" }}>
                  <TableCell
                    sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap", color: "text.secondary" }}
                  >
                    {record.time ? formatDateTime(record.time) : "—"}
                  </TableCell>
                  <TableCell>
                    <LevelChip level={record.level} />
                  </TableCell>
                  <TableCell sx={{ whiteSpace: "nowrap", color: "text.secondary" }}>
                    {record.name ?? "—"}
                  </TableCell>
                  <TableCell sx={{ width: "100%" }}>
                    <Box component="span" sx={{ fontFamily: MONO_FONT, fontSize: "0.8125rem" }}>
                      {record.message}
                    </Box>
                    {record.traceback && (
                      <Box
                        component="details"
                        sx={{ mt: 0.5, "& summary": { cursor: "pointer", fontSize: "0.8125rem" } }}
                      >
                        <summary>Traceback</summary>
                        <Box
                          component="pre"
                          sx={{
                            fontFamily: MONO_FONT,
                            fontSize: "0.75rem",
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-word",
                            bgcolor: "action.hover",
                            p: 1.5,
                            borderRadius: 1,
                            m: 0,
                            mt: 0.5,
                          }}
                        >
                          {record.traceback}
                        </Box>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Page>
  );
}
