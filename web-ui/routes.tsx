import { Navigate, Route, Routes, useParams } from "react-router";
import { PrivacyGate } from "@/components/privacy-gate";
import { MainLayout } from "@/layout/main-layout";
import { MinimalLayout } from "@/layout/minimal-layout";
import { ActivateView } from "@/views/auth/activate-view";
import { ConfirmEmailView } from "@/views/auth/confirm-email-view";
import { LoginView } from "@/views/auth/login-view";
import { LogoutView } from "@/views/auth/logout-view";
import { PasswordResetConfirmView } from "@/views/auth/password-reset-confirm-view";
import { PasswordResetView } from "@/views/auth/password-reset-view";
import { RegisterView } from "@/views/auth/register-view";
import { HomeView } from "@/views/home-view";

function RedirectWithParam({ to }: { to: (params: Record<string, string | undefined>) => string }) {
  const params = useParams();
  return <Navigate to={to(params)} replace />;
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

      {/* Main site: gated by the site privacy setting. */}
      <Route
        element={
          <PrivacyGate>
            <MainLayout />
          </PrivacyGate>
        }
      >
        <Route path="/" element={<HomeView />} />
        <Route path="/accounts/logout" element={<LogoutView />} />
      </Route>

      {/* Legacy short URLs. */}
      <Route path="/drink/:id" element={<RedirectWithParam to={(p) => `/drinks/${p.id}`} />} />
      <Route path="/d/:id" element={<RedirectWithParam to={(p) => `/drinks/${p.id}`} />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
