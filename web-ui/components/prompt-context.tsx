import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import { createContext, type ReactNode, useCallback, useContext, useRef, useState } from "react";

export interface PromptOptions {
  title: string;
  /** Input label ("Volume (mL)"). */
  label: string;
  initialValue?: string;
  confirmText?: string;
  /** HTML input type; "number" and "password" are the common ones. */
  type?: string;
  helperText?: string;
}

type PromptFn = (options: PromptOptions) => Promise<string | null>;

const PromptContext = createContext<PromptFn>(null as unknown as PromptFn);

/**
 * Promise-based single-input dialogs (the civilized window.prompt):
 *
 *   const prompt = usePrompt();
 *   const volume = await prompt({ title: "Record spill", label: "Volume (mL)", type: "number" });
 *   if (volume !== null) { ... }
 */
export function PromptProvider({ children }: { children: ReactNode }) {
  const [options, setOptions] = useState<PromptOptions | null>(null);
  const [value, setValue] = useState("");
  const resolver = useRef<((result: string | null) => void) | null>(null);

  const prompt = useCallback<PromptFn>((opts) => {
    setOptions(opts);
    setValue(opts.initialValue ?? "");
    return new Promise<string | null>((resolve) => {
      resolver.current = resolve;
    });
  }, []);

  const close = (result: string | null) => {
    setOptions(null);
    resolver.current?.(result);
    resolver.current = null;
  };

  return (
    <PromptContext.Provider value={prompt}>
      {children}
      <Dialog open={options !== null} onClose={() => close(null)} maxWidth="xs" fullWidth>
        <DialogTitle>{options?.title}</DialogTitle>
        <DialogContent>
          <form
            id="prompt-dialog-form"
            onSubmit={(e) => {
              e.preventDefault();
              close(value);
            }}
          >
            <TextField
              autoFocus
              fullWidth
              margin="dense"
              label={options?.label}
              type={options?.type ?? "text"}
              value={value}
              helperText={options?.helperText}
              onChange={(e) => setValue(e.target.value)}
            />
          </form>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => close(null)}>Cancel</Button>
          <Button type="submit" form="prompt-dialog-form" variant="contained">
            {options?.confirmText ?? "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </PromptContext.Provider>
  );
}

export function usePrompt(): PromptFn {
  return useContext(PromptContext);
}
