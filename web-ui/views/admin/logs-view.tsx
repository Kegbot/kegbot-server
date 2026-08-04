import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import FormControlLabel from "@mui/material/FormControlLabel";
import Stack from "@mui/material/Stack";
import Switch from "@mui/material/Switch";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { useState } from "react";
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

/** "05:54:29" — logs are recent; the full date lives in the tooltip. */
function timeOfDay(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

const CHIP_COLORS: Record<string, "default" | "info" | "warning" | "error"> = {
  debug: "default",
  info: "info",
  warning: "warning",
  error: "error",
  critical: "error",
};

/** Text colors for the dense line view. */
const TEXT_COLORS: Record<string, string> = {
  debug: "text.disabled",
  info: "info.main",
  warning: "warning.main",
  error: "error.main",
  critical: "error.main",
};

function LevelChip({ level }: { level?: string }) {
  if (!level) {
    return null;
  }
  return (
    <Chip
      label={level.toUpperCase()}
      color={CHIP_COLORS[level.toLowerCase()] ?? "default"}
      size="small"
      variant="outlined"
      sx={{ fontFamily: MONO_FONT, fontSize: "0.6875rem" }}
    />
  );
}

function Traceback({ text }: { text: string }) {
  return (
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
        {text}
      </Box>
    </Box>
  );
}

/** Terminal-style stream: one wrapped line per record. */
function DenseLogList({ records }: { records: LogRecord[] }) {
  return (
    <Box sx={{ fontFamily: MONO_FONT, fontSize: "0.75rem", lineHeight: 1.7 }}>
      {records.map((record, index) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: records have no id
        <Box key={index} sx={{ wordBreak: "break-word" }}>
          {record.time && (
            <Box component="span" sx={{ color: "text.secondary" }} title={record.time}>
              {timeOfDay(record.time)}{" "}
            </Box>
          )}
          {record.level && (
            <Box
              component="span"
              sx={{ color: TEXT_COLORS[record.level.toLowerCase()] ?? "text.secondary" }}
            >
              {record.level.toUpperCase().padEnd(7)}{" "}
            </Box>
          )}
          {record.name && (
            <Box component="span" sx={{ color: "text.secondary" }}>
              {record.name}{" "}
            </Box>
          )}
          <Box component="span">{record.message}</Box>
          {record.traceback && <Traceback text={record.traceback} />}
        </Box>
      ))}
    </Box>
  );
}

function LogTable({ records }: { records: LogRecord[] }) {
  return (
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
                title={record.time ? formatDateTime(record.time) : undefined}
              >
                {record.time ? timeOfDay(record.time) : "—"}
              </TableCell>
              <TableCell>
                <LevelChip level={record.level} />
              </TableCell>
              <TableCell
                sx={{
                  color: "text.secondary",
                  maxWidth: 140,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={record.name}
              >
                {record.name ?? "—"}
              </TableCell>
              <TableCell sx={{ width: "100%" }}>
                <Box component="span" sx={{ fontFamily: MONO_FONT, fontSize: "0.8125rem" }}>
                  {record.message}
                </Box>
                {record.traceback && <Traceback text={record.traceback} />}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

const DENSE_KEY = "kb:logs:dense";

export function LogsView() {
  const logs = useAsyncData(
    async () => (await unwrap(adminLogsRetrieve())) as unknown as LogsPayload,
  );
  const [dense, setDense] = useState(() => localStorage.getItem(DENSE_KEY) === "1");
  const records = (logs.data?.logs ?? []).map(parseRecord);

  const toggleDense = (value: boolean) => {
    setDense(value);
    localStorage.setItem(DENSE_KEY, value ? "1" : "0");
  };

  return (
    <Page
      title="Logs"
      loading={logs.loading}
      error={logs.error}
      headerRight={
        <FormControlLabel
          control={
            <Switch size="small" checked={dense} onChange={(e) => toggleDense(e.target.checked)} />
          }
          label="Dense"
          slotProps={{ typography: { variant: "body2", color: "text.secondary" } }}
        />
      }
    >
      <Stack spacing={2}>
        {logs.data?.error && <Alert severity="warning">{logs.data.error}</Alert>}
        {logs.data && records.length === 0 && !logs.data.error && (
          <Typography color="text.secondary">No recent log records.</Typography>
        )}
        {records.length > 0 &&
          (dense ? <DenseLogList records={records} /> : <LogTable records={records} />)}
      </Stack>
    </Page>
  );
}
