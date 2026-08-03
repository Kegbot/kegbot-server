import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { useState } from "react";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { ConfigProvider } from "@/components/config-context";
import { ConfirmProvider } from "@/components/confirm-context";
import { CurrentUserProvider } from "@/components/current-user-context";
import { SnackbarProvider } from "@/components/snackbar-context";
import { AppRoutes } from "@/routes";
import { theme } from "@/theme/theme";

export function App() {
  // A single splat route delegates to a classic <Routes> tree; the data
  // router wrapper keeps navigation-blocking hooks available later. The
  // router is created per mount so it reads the current location.
  const [router] = useState(() => createBrowserRouter([{ path: "*", element: <AppRoutes /> }]));
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider>
        <ConfigProvider>
          <CurrentUserProvider>
            <ConfirmProvider>
              <RouterProvider router={router} />
            </ConfirmProvider>
          </CurrentUserProvider>
        </ConfigProvider>
      </SnackbarProvider>
    </ThemeProvider>
  );
}
