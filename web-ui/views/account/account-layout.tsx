import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import { Link, Outlet, useLocation } from "react-router";
import { useConfig } from "@/components/config-context";

/** Account section chrome: tab bar over the active account view. */
export function AccountLayout() {
  const { me } = useConfig();
  const location = useLocation();

  const tabs = [
    { label: "Account", to: "/account" },
    { label: "Profile", to: "/account/profile" },
    { label: "Password", to: "/account/password" },
    { label: "Notifications", to: "/account/notifications" },
    ...(me.can_invite ? [{ label: "Invite", to: "/account/invite" }] : []),
  ];

  const active = tabs.reduce(
    (best, tab) =>
      location.pathname.startsWith(tab.to) && tab.to.length > best.length ? tab.to : best,
    "/account",
  );

  return (
    <Stack spacing={2}>
      <Tabs value={active} variant="scrollable" allowScrollButtonsMobile>
        {tabs.map((tab) => (
          <Tab key={tab.to} label={tab.label} value={tab.to} component={Link} to={tab.to} />
        ))}
      </Tabs>
      <Outlet />
    </Stack>
  );
}
