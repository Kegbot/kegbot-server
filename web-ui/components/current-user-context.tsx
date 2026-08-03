import { createContext, type ReactNode, useContext, useMemo } from "react";
import type { CurrentUser } from "@/api";
import { authLoginCreate, authLogoutCreate } from "@/api";
import { useConfig } from "@/components/config-context";
import { unwrap } from "@/lib/api";

export interface CurrentUserValue {
  user: CurrentUser | null;
  isLoggedIn: boolean;
  isStaff: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const CurrentUserContext = createContext<CurrentUserValue>(null as unknown as CurrentUserValue);

export function CurrentUserProvider({ children }: { children: ReactNode }) {
  const { me, refresh } = useConfig();

  const value = useMemo<CurrentUserValue>(
    () => ({
      user: me.user,
      isLoggedIn: me.user !== null,
      isStaff: me.user?.is_staff ?? false,
      login: async (username, password) => {
        await unwrap(authLoginCreate({ body: { username, password } }));
        await refresh();
      },
      logout: async () => {
        await unwrap(authLogoutCreate());
        await refresh();
      },
      refresh,
    }),
    [me.user, refresh],
  );

  return <CurrentUserContext.Provider value={value}>{children}</CurrentUserContext.Provider>;
}

export function useCurrentUser(): CurrentUserValue {
  return useContext(CurrentUserContext);
}
