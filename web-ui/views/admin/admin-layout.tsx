import { Outlet } from "react-router";
import { useConfig } from "@/components/config-context";
import { SideNavLayout, type SideNavSection } from "@/layout/side-nav-layout";

function useNavSections(): SideNavSection[] {
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
  ].filter((section) => section.items.length > 0);
}

export function AdminLayout() {
  const sections = useNavSections();
  return (
    <SideNavLayout sections={sections}>
      <Outlet />
    </SideNavLayout>
  );
}
