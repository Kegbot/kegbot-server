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
import { useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router";
import { ColorModeToggle } from "@/components/color-mode-toggle";
import { useConfig } from "@/components/config-context";
import { useCurrentUser } from "@/components/current-user-context";
import { Footer } from "@/components/footer";
import { Wordmark } from "@/components/wordmark";

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
          <Avatar src={mugshotUrl} sx={{ width: 30, height: 30 }} />
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

const NAV_ITEMS: Array<{ label: string; to: string }> = [
  { label: "Kegs", to: "/kegs" },
  { label: "Sessions", to: "/sessions" },
  { label: "Stats", to: "/stats" },
];

function NavButton({ label, to }: { label: string; to: string }) {
  const location = useLocation();
  const active = location.pathname === to || location.pathname.startsWith(`${to}/`);
  return (
    <Button
      component={Link}
      to={to}
      size="small"
      sx={{
        color: active ? "text.primary" : "text.secondary",
        px: 1.25,
        "&:hover": { color: "text.primary", bgcolor: "transparent" },
      }}
    >
      {label}
    </Button>
  );
}

export function MainLayout() {
  const { me } = useConfig();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <AppBar
        position="sticky"
        sx={{
          bgcolor: "background.paper",
          color: "text.primary",
          borderBottom: 1,
          borderColor: "divider",
          backgroundImage: "none",
        }}
      >
        <Toolbar variant="dense" sx={{ gap: 1, minHeight: 56 }}>
          <Box component={Link} to="/" sx={{ textDecoration: "none", mr: 2, minWidth: 0 }}>
            <Wordmark siteTitle={me.site.title} />
          </Box>
          <Box sx={{ display: "flex", gap: 0.5, overflowX: "auto", flexGrow: 1 }}>
            {NAV_ITEMS.map((item) => (
              <NavButton key={item.to} {...item} />
            ))}
          </Box>
          <ColorModeToggle />
          <UserMenu />
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: { xs: 2.5, md: 4 }, flexGrow: 1 }}>
        <Outlet />
      </Container>
      <Footer />
    </Box>
  );
}
