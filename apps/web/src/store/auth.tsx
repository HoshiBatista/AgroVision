import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import * as apiClient from "../api/client";
import type { AuthUser } from "../api/types";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function bootstrap() {
      if (!apiClient.tokenStore.access()) {
        setLoading(false);
        return;
      }
      try {
        const me = await apiClient.fetchMe();
        if (active) setUser(me);
      } catch {
        apiClient.tokenStore.clear();
      } finally {
        if (active) setLoading(false);
      }
    }
    void bootstrap();
    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login: async (email, password) => {
        await apiClient.login(email, password);
        setUser(await apiClient.fetchMe());
      },
      register: async (email, password) => {
        await apiClient.register(email, password);
        setUser(await apiClient.fetchMe());
      },
      logout: () => {
        apiClient.tokenStore.clear();
        setUser(null);
      },
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
