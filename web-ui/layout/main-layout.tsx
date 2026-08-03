import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router";
import { useConfig } from "@/components/config-context";
import { useCurrentUser } from "@/components/current-user-context";

function UserMenu() {
  const { me } = useConfig();
  const { user } = useCurrentUser();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);

  if (!user) {
    if (me.sso_login_url) {
      const redir = encodeURIComponent(window.location.origin + location.pathname);
      return (
        <Button color="inherit" href={`${me.sso_login_url}?redir=${redir}`}>
          Log in
        </Button>
      );
    }
    return (
      <Button
        color="inherit"
        component={Link}
        to={`/accounts/login?next=${encodeURIComponent(location.pathname)}`}
      >
        Log in
      </Button>
    );
  }

  const mugshotUrl = user.picture?.thumbnail_url;
  return (
    <>
      <IconButton color="inherit" onClick={(e) => setAnchor(e.currentTarget)} size="large">
        {mugshotUrl ? (
          <Avatar src={mugshotUrl} sx={{ width: 32, height: 32 }} />
        ) : (
          <AccountCircleIcon />
        )}
      </IconButton>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}>
        <MenuItem disabled>{user.display_name || user.username}</MenuItem>
        <MenuItem
          onClick={() => {
            setAnchor(null);
            navigate("/account");
          }}
        >
          My account
        </MenuItem>
        {user.is_staff && (
          <MenuItem
            onClick={() => {
              setAnchor(null);
              navigate("/kegadmin");
            }}
          >
            Admin
          </MenuItem>
        )}
        <MenuItem
          onClick={() => {
            setAnchor(null);
            navigate("/accounts/logout");
          }}
        >
          Log out
        </MenuItem>
      </Menu>
    </>
  );
}

export function MainLayout() {
  const { me } = useConfig();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar position="sticky">
        <Toolbar>
          <Typography
            variant="h6"
            component={Link}
            to="/"
            sx={{ color: "inherit", textDecoration: "none", flexGrow: 1 }}
          >
            {me.site.title}
          </Typography>
          <UserMenu />
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 }, flexGrow: 1 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
