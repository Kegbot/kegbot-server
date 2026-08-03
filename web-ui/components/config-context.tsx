import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from "react";
import type { Me } from "@/api-client";
import { usersMeRetrieve } from "@/api-client";
import { toErrorMessage, unwrap } from "@/lib/api";

export interface ConfigValue {
  /** The boot payload; always present once the app renders. */
  me: Me;
  /** Refetches the boot payload (e.g. after login/logout/profile edit). */
  refresh: () => Promise<void>;
}

const ConfigContext = createContext<ConfigValue>(null as unknown as ConfigValue);

type BootState =
  | { status: "loading" }
  | { status: "ready"; me: Me }
  | { status: "setup"; kind: "setup_required" | "upgrade_required" }
  | { status: "error"; message: string };

function isSetupError(error: unknown): "setup_required" | "upgrade_required" | null {
  if (error && typeof error === "object") {
    const kind = (error as { error?: unknown }).error;
    if (kind === "setup_required" || kind === "upgrade_required") {
      return kind;
    }
  }
  return null;
}

export interface ConfigProviderProps {
  children: ReactNode;
  /** Rendered instead of the app when the server needs setup/upgrade. */
  renderSetup?: (kind: "setup_required" | "upgrade_required") => ReactNode;
}

/**
 * Boots the app: fetches /api/users/me (which also sets the CSRF
 * cookie) and blocks rendering until it resolves. Children never render
 * without a boot payload.
 */
export function ConfigProvider({ children, renderSetup }: ConfigProviderProps) {
  const [state, setState] = useState<BootState>({ status: "loading" });

  const load = useCallback(async () => {
    try {
      const me = await unwrap(usersMeRetrieve());
      setState({ status: "ready", me });
    } catch (error) {
      const setupKind = isSetupError(error);
      if (setupKind) {
        setState({ status: "setup", kind: setupKind });
      } else {
        setState({ status: "error", message: toErrorMessage(error) });
      }
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (state.status === "loading") {
    return (
      <Box
        sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (state.status === "setup") {
    return (
      <>
        {renderSetup?.(state.kind) ?? (
          <Box sx={{ p: 4 }}>
            <Alert severity="info">
              {state.kind === "setup_required"
                ? "This server needs to be set up."
                : "This server needs an upgrade."}
            </Alert>
          </Box>
        )}
      </>
    );
  }

  if (state.status === "error") {
    return (
      <Box sx={{ p: 4, display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
        <Alert severity="error">Could not reach the server: {state.message}</Alert>
        <Button variant="contained" onClick={() => void load()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <ConfigContext.Provider value={{ me: state.me, refresh: load }}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig(): ConfigValue {
  return useContext(ConfigContext);
}
