import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import { Outlet } from "react-router";

/** Chrome-free layout for auth, setup, and fullscreen views. */
export function MinimalLayout() {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
