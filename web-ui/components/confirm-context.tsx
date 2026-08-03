import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { createContext, type ReactNode, useCallback, useContext, useRef, useState } from "react";

export interface ConfirmOptions {
  title: string;
  message?: string;
  confirmText?: string;
  /** Style the confirm button as destructive (red). */
  destructive?: boolean;
}

type ConfirmFn = (options: ConfirmOptions) => Promise<boolean>;

const ConfirmContext = createContext<ConfirmFn>(null as unknown as ConfirmFn);

/**
 * Promise-based confirmation dialogs:
 *
 *   const confirm = useConfirm();
 *   if (await confirm({ title: "End keg?", destructive: true })) { ... }
 */
export function ConfirmProvider({ children }: { children: ReactNode }) {
  const [options, setOptions] = useState<ConfirmOptions | null>(null);
  const resolver = useRef<((result: boolean) => void) | null>(null);

  const confirm = useCallback<ConfirmFn>((opts) => {
    setOptions(opts);
    return new Promise<boolean>((resolve) => {
      resolver.current = resolve;
    });
  }, []);

  const close = (result: boolean) => {
    setOptions(null);
    resolver.current?.(result);
    resolver.current = null;
  };

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      <Dialog open={options !== null} onClose={() => close(false)} maxWidth="xs" fullWidth>
        <DialogTitle>{options?.title}</DialogTitle>
        {options?.message && (
          <DialogContent>
            <DialogContentText>{options.message}</DialogContentText>
          </DialogContent>
        )}
        <DialogActions>
          <Button onClick={() => close(false)}>Cancel</Button>
          <Button
            onClick={() => close(true)}
            variant="contained"
            color={options?.destructive ? "error" : "primary"}
            autoFocus
          >
            {options?.confirmText ?? "Confirm"}
          </Button>
        </DialogActions>
      </Dialog>
    </ConfirmContext.Provider>
  );
}

export function useConfirm(): ConfirmFn {
  return useContext(ConfirmContext);
}
