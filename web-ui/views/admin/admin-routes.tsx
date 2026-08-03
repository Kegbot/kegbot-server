import { Navigate, Route, Routes } from "react-router";
import { AdminLayout } from "@/views/admin/admin-layout";
import { BeveragesView } from "@/views/admin/beverages-view";
import { BugreportView } from "@/views/admin/bugreport-view";
import { ControllersView } from "@/views/admin/controllers-view";
import { DashboardView } from "@/views/admin/dashboard-view";
import { DrinksAdminView } from "@/views/admin/drinks-admin-view";
import { EmailView } from "@/views/admin/email-view";
import { ExportView } from "@/views/admin/export-view";
import { KegsAdminView } from "@/views/admin/kegs-admin-view";
import { LogsView } from "@/views/admin/logs-view";
import { PluginSettingsView } from "@/views/admin/plugin-settings-view";
import { ProducersView } from "@/views/admin/producers-view";
import { SettingsAdvancedView } from "@/views/admin/settings-advanced-view";
import { SettingsGeneralView } from "@/views/admin/settings-general-view";
import { SettingsLocationView } from "@/views/admin/settings-location-view";
import { TapDetailView } from "@/views/admin/tap-detail-view";
import { TapsView } from "@/views/admin/taps-view";
import { TokensView } from "@/views/admin/tokens-view";
import { UsersAdminView } from "@/views/admin/users-admin-view";

/** Routes under /kegadmin (lazy-loaded; staff-only via RequireAuth). */
export default function AdminRoutes() {
  return (
    <Routes>
      <Route element={<AdminLayout />}>
        <Route index element={<DashboardView />} />
        <Route path="settings/general" element={<SettingsGeneralView />} />
        <Route path="settings/location" element={<SettingsLocationView />} />
        <Route path="settings/advanced" element={<SettingsAdvancedView />} />
        <Route path="email" element={<EmailView />} />
        <Route path="controllers" element={<ControllersView />} />
        <Route path="taps" element={<TapsView />} />
        <Route path="taps/:id" element={<TapDetailView />} />
        <Route path="kegs" element={<KegsAdminView />} />
        <Route path="drinks" element={<DrinksAdminView />} />
        <Route path="users" element={<UsersAdminView />} />
        <Route path="tokens" element={<TokensView />} />
        <Route path="beers" element={<BeveragesView />} />
        <Route path="brewers" element={<ProducersView />} />
        <Route path="plugin/:name" element={<PluginSettingsView />} />
        <Route path="logs" element={<LogsView />} />
        <Route path="bugreport" element={<BugreportView />} />
        <Route path="export" element={<ExportView />} />
        <Route path="*" element={<Navigate to="/kegadmin" replace />} />
      </Route>
    </Routes>
  );
}
