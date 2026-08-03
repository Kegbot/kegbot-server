import Alert, { type AlertColor } from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from "react";

export interface SnackbarValue {
  showMessage: (message: string, severity?: AlertColor) => void;
}

const SnackbarContext = createContext<SnackbarValue>(null as unknown as SnackbarValue);

interface Message {
  id: number;
  text: string;
  severity: AlertColor;
}

let nextId = 1;

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [current, setCurrent] = useState<Message | null>(null);

  const showMessage = useCallback((text: string, severity: AlertColor = "success") => {
    setCurrent({ id: nextId++, text, severity });
  }, []);

  const value = useMemo(() => ({ showMessage }), [showMessage]);

  return (
    <SnackbarContext.Provider value={value}>
      {children}
      <Snackbar
        key={current?.id}
        open={current !== null}
        autoHideDuration={5000}
        onClose={(_, reason) => {
          if (reason !== "clickaway") {
            setCurrent(null);
          }
        }}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        {current ? (
          <Alert severity={current.severity} onClose={() => setCurrent(null)} variant="filled">
            {current.text}
          </Alert>
        ) : undefined}
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export function useSnackbar(): SnackbarValue {
  return useContext(SnackbarContext);
}
