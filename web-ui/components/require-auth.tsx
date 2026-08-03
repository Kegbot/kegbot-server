import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import { useCurrentUser } from "@/components/current-user-context";

/** Redirects anonymous users to login (with a return path). */
export function RequireAuth({ children, staff = false }: { children: ReactNode; staff?: boolean }) {
  const { user } = useCurrentUser();
  const location = useLocation();

  if (!user) {
    return (
      <Navigate to={`/accounts/login?next=${encodeURIComponent(location.pathname)}`} replace />
    );
  }
  if (staff && !user.is_staff) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
