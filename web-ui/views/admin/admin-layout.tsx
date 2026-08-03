import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import Paper from "@mui/material/Paper";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import { Link, Outlet, useLocation } from "react-router";
import { useConfig } from "@/components/config-context";

interface NavEntry {
  label: string;
  to: string;
}

interface NavSection {
  header: string;
  items: NavEntry[];
}

function useNavSections(): NavSection[] {
  const { me } = useConfig();
  const sensing = me.site.enable_sensing ?? true;
  const users = me.site.enable_users ?? true;
  return [
    { header: "Overview", items: [{ label: "Dashboard", to: "/kegadmin" }] },
    {
      header: "Settings",
      items: [
        { label: "General", to: "/kegadmin/settings/general" },
        { label: "Location", to: "/kegadmin/settings/location" },
        { label: "Advanced", to: "/kegadmin/settings/advanced" },
        { label: "E-mail", to: "/kegadmin/email" },
      ],
    },
    {
      header: "System",
      items: [
        ...(sensing ? [{ label: "Controllers", to: "/kegadmin/controllers" }] : []),
        { label: "Taps", to: "/kegadmin/taps" },
        { label: "Keg Room", to: "/kegadmin/kegs" },
        ...(sensing ? [{ label: "Drinks", to: "/kegadmin/drinks" }] : []),
        ...(users ? [{ label: "Users", to: "/kegadmin/users" }] : []),
        ...(users ? [{ label: "Tokens", to: "/kegadmin/tokens" }] : []),
      ],
    },
    {
      header: "Beer Database",
      items: [
        { label: "Beverages", to: "/kegadmin/beers" },
        { label: "Producers", to: "/kegadmin/brewers" },
      ],
    },
    {
      header: "Plugins",
      items: me.plugins.map((plugin) => ({
        label: plugin.name,
        to: `/kegadmin/plugin/${plugin.short_name}`,
      })),
    },
    {
      header: "Maintenance",
      items: [
        { label: "Logs", to: "/kegadmin/logs" },
        { label: "Bug Report", to: "/kegadmin/bugreport" },
        { label: "Backup / Export", to: "/kegadmin/export" },
      ],
    },
  ];
}

export function AdminLayout() {
  const sections = useNavSections();
  const location = useLocation();
  const theme = useTheme();
  const narrow = useMediaQuery(theme.breakpoints.down("md"));

  const allItems = sections.flatMap((s) => s.items);
  const active = allItems.reduce(
    (best, item) =>
      location.pathname === item.to ||
      (location.pathname.startsWith(`${item.to}/`) && item.to.length > best.length)
        ? item.to
        : best,
    "/kegadmin",
  );

  const nav = (
    <List dense sx={{ minWidth: 200 }}>
      {sections.map((section) =>
        section.items.length === 0 ? null : (
          <Box key={section.header}>
            <ListSubheader disableSticky>{section.header}</ListSubheader>
            {section.items.map((item) => (
              <ListItemButton
                key={item.to}
                component={Link}
                to={item.to}
                selected={active === item.to}
              >
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}
            <Divider component="li" sx={{ my: 0.5 }} />
          </Box>
        ),
      )}
    </List>
  );

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: narrow ? "column" : "row",
        gap: 3,
        alignItems: "flex-start",
      }}
    >
      <Paper variant="outlined" sx={{ width: narrow ? "100%" : 220, flexShrink: 0 }}>
        {nav}
      </Paper>
      <Box sx={{ flexGrow: 1, width: "100%", minWidth: 0 }}>
        <Outlet />
      </Box>
    </Box>
  );
}
