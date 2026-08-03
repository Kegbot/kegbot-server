import { Outlet } from "react-router";
import { useConfig } from "@/components/config-context";
import { SideNavLayout } from "@/layout/side-nav-layout";

/** Account section chrome: shared side navigation (same as admin). */
export function AccountLayout() {
  const { me } = useConfig();

  const items = [
    { label: "Account", to: "/account" },
    { label: "Profile", to: "/account/profile" },
    { label: "Password", to: "/account/password" },
    { label: "Notifications", to: "/account/notifications" },
    ...(me.can_invite ? [{ label: "Invite", to: "/account/invite" }] : []),
  ];

  return (
    <SideNavLayout sections={[{ header: "My account", items }]}>
      <Outlet />
    </SideNavLayout>
  );
}
