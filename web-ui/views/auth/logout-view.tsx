import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";
import { useCurrentUser } from "@/components/current-user-context";

export function LogoutView() {
  const { isLoggedIn, logout } = useCurrentUser();
  const navigate = useNavigate();
  const started = useRef(false);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/", { replace: true });
      return;
    }
    if (started.current) {
      return;
    }
    started.current = true;
    void logout().finally(() => navigate("/", { replace: true }));
  }, [isLoggedIn, logout, navigate]);

  return (
    <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
      <CircularProgress />
    </Box>
  );
}
