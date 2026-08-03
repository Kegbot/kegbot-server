import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import { Link, Outlet } from "react-router";
import { Wordmark } from "@/components/wordmark";

/** Chrome-free layout for auth, setup, and token-link views. */
export function MinimalLayout() {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center" }}>
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Box
          component={Link}
          to="/"
          sx={{ display: "flex", justifyContent: "center", mb: 3, textDecoration: "none" }}
        >
          <Wordmark />
        </Box>
        <Outlet />
      </Container>
    </Box>
  );
}
