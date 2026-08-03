import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";
import { AppRoutes } from "@/routes";
import { theme } from "@/theme/theme";

// A single splat route delegates to a classic <Routes> tree; the data
// router wrapper keeps navigation-blocking hooks available later.
const router = createBrowserRouter([{ path: "*", element: <AppRoutes /> }]);

export function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RouterProvider router={router} />
    </ThemeProvider>
  );
}
