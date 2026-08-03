import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import { lazy, Suspense } from "react";
import { Navigate, Route, Routes, useParams } from "react-router";
import { PrivacyGate } from "@/components/privacy-gate";
import { RequireAuth } from "@/components/require-auth";
import { MainLayout } from "@/layout/main-layout";
import { MinimalLayout } from "@/layout/minimal-layout";
import { AccountLayout } from "@/views/account/account-layout";
import { AccountView } from "@/views/account/account-view";
import { InviteView } from "@/views/account/invite-view";
import { NotificationsView } from "@/views/account/notifications-view";
import { PasswordView } from "@/views/account/password-view";
import { ProfileView } from "@/views/account/profile-view";
import { ActivateView } from "@/views/auth/activate-view";
import { ConfirmEmailView } from "@/views/auth/confirm-email-view";
import { LoginView } from "@/views/auth/login-view";
import { LogoutView } from "@/views/auth/logout-view";
import { PasswordResetConfirmView } from "@/views/auth/password-reset-confirm-view";
import { PasswordResetView } from "@/views/auth/password-reset-view";
import { RegisterView } from "@/views/auth/register-view";
import { DrinkerView } from "@/views/drinkers/drinker-view";
import { DrinkView } from "@/views/drinks/drink-view";
import { FullscreenView } from "@/views/fullscreen-view";
import { HomeView } from "@/views/home-view";
import { KegDetailView } from "@/views/kegs/keg-detail-view";
import { KegListView } from "@/views/kegs/keg-list-view";
import { SessionDetailView } from "@/views/sessions/session-detail-view";
import { SessionListView } from "@/views/sessions/session-list-view";
import { StatsView } from "@/views/stats-view";

function RedirectWithParam({ to }: { to: (params: Record<string, string | undefined>) => string }) {
  const params = useParams();
  return <Navigate to={to(params)} replace />;
}

// The admin area loads as its own chunk; staff-only.
const AdminRoutes = lazy(() => import("@/views/admin/admin-routes"));

function AdminFallback() {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
      <CircularProgress />
    </Box>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      {/* Auth and token-link flows: never privacy-gated. */}
      <Route element={<MinimalLayout />}>
        <Route path="/accounts/login" element={<LoginView />} />
        <Route path="/accounts/register" element={<RegisterView />} />
        <Route path="/accounts/password/reset" element={<PasswordResetView />} />
        <Route
          path="/accounts/password/reset/confirm/:combined"
          element={<PasswordResetConfirmView />}
        />
        <Route path="/account/activate/:key" element={<ActivateView />} />
        <Route path="/account/confirm-email/:token" element={<ConfirmEmailView />} />
      </Route>

      {/* Kiosk mode: gated but chrome-free. */}
      <Route
        path="/fullscreen"
        element={
          <PrivacyGate>
            <FullscreenView />
          </PrivacyGate>
        }
      />

      {/* Main site: gated by the site privacy setting. */}
      <Route
        element={
          <PrivacyGate>
            <MainLayout />
          </PrivacyGate>
        }
      >
        <Route path="/" element={<HomeView />} />
        <Route path="/stats" element={<StatsView />} />
        <Route path="/kegs" element={<KegListView />} />
        <Route path="/kegs/:id" element={<KegDetailView />} />
        <Route
          path="/kegs/:id/sessions"
          element={<RedirectWithParam to={(p) => `/kegs/${p.id}`} />}
        />
        <Route path="/drinkers/:username" element={<DrinkerView />} />
        <Route
          path="/drinkers/:username/sessions"
          element={<RedirectWithParam to={(p) => `/drinkers/${p.username}`} />}
        />
        <Route path="/drinks/:id" element={<DrinkView />} />
        <Route path="/sessions" element={<SessionListView />} />
        <Route path="/sessions/:year" element={<SessionListView />} />
        <Route path="/sessions/:year/:month" element={<SessionListView />} />
        <Route path="/sessions/:year/:month/:day" element={<SessionListView />} />
        <Route path="/sessions/id/:id" element={<SessionDetailView />} />
        <Route path="/sessions/:year/:month/:day/:id" element={<SessionDetailView />} />
        <Route path="/accounts/logout" element={<LogoutView />} />
        <Route
          path="/account"
          element={
            <RequireAuth>
              <AccountLayout />
            </RequireAuth>
          }
        >
          <Route index element={<AccountView />} />
          <Route path="profile" element={<ProfileView />} />
          <Route path="password" element={<PasswordView />} />
          <Route path="notifications" element={<NotificationsView />} />
          <Route path="invite" element={<InviteView />} />
        </Route>
        <Route
          path="/kegadmin/*"
          element={
            <RequireAuth staff>
              <Suspense fallback={<AdminFallback />}>
                <AdminRoutes />
              </Suspense>
            </RequireAuth>
          }
        />
      </Route>

      {/* Legacy short URLs. */}
      <Route path="/drink/:id" element={<RedirectWithParam to={(p) => `/drinks/${p.id}`} />} />
      <Route path="/d/:id" element={<RedirectWithParam to={(p) => `/drinks/${p.id}`} />} />
      <Route path="/s/:id" element={<RedirectWithParam to={(p) => `/sessions/id/${p.id}`} />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
