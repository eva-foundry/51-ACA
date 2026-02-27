/**
 * useAuth -- lightweight auth hook for ACA frontend.
 *
 * Two modes:
 *   1. VITE_DEV_AUTH=true  -- dev bypass; reads roles + subscriptionId from env vars.
 *   2. Production          -- wraps MSAL PublicClientApplication (TODO: wire MSAL).
 *
 * The hook is intentionally minimal. Real MSAL integration is an Epic 5 milestone.
 * For now it surfaces the shape expected by RequireAuth and RequireRole.
 */

import { useState, useCallback } from "react";
import type { AcaRole } from "./roles";

export interface AuthUser {
  userId: string;
  upn: string;
  roles: AcaRole[];
  subscriptionId: string | null;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// ---------------------------------------------------------------------------
// Dev bypass mode
// ---------------------------------------------------------------------------
function devBypassUser(): AuthUser {
  const sub = import.meta.env.VITE_DEV_SUBSCRIPTION_ID ?? "dev-subscription-001";
  const rawRoles = import.meta.env.VITE_DEV_ROLES ?? "";
  const roles = rawRoles
    ? rawRoles.split(",").map((r: string) => r.trim() as AcaRole)
    : [];
  return {
    userId: "dev-user-001",
    upn: "dev@aca.local",
    roles,
    subscriptionId: sub,
  };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------
export function useAuth(): AuthState & {
  login: () => Promise<void>;
  logout: () => void;
  hasRole: (...roles: AcaRole[]) => boolean;
} {
  const isDevAuth = import.meta.env.VITE_DEV_AUTH === "true";

  const [state, setState] = useState<AuthState>(() => {
    if (isDevAuth) {
      return { user: devBypassUser(), isAuthenticated: true, isLoading: false };
    }
    // Real MSAL: check session on mount (simplified -- no MSAL SDK wired yet)
    const stored = sessionStorage.getItem("aca_auth_user");
    if (stored) {
      try {
        return { user: JSON.parse(stored) as AuthUser, isAuthenticated: true, isLoading: false };
      } catch {
        // invalid cache -- fall through
      }
    }
    return { user: null, isAuthenticated: false, isLoading: false };
  });

  const login = useCallback(async () => {
    if (isDevAuth) {
      const u = devBypassUser();
      sessionStorage.setItem("aca_auth_user", JSON.stringify(u));
      setState({ user: u, isAuthenticated: true, isLoading: false });
      return;
    }
    // TODO: wire real MSAL login (PublicClientApplication.loginRedirect)
    // For MVP dev sprint, this is a no-op placeholder.
    console.warn("useAuth.login: MSAL not wired. Set VITE_DEV_AUTH=true for local dev.");
  }, [isDevAuth]);

  const logout = useCallback(() => {
    sessionStorage.removeItem("aca_auth_user");
    setState({ user: null, isAuthenticated: false, isLoading: false });
  }, []);

  const hasRole = useCallback(
    (...roles: AcaRole[]) => {
      if (!state.user) return false;
      return roles.some((r) => state.user!.roles.includes(r));
    },
    [state.user]
  );

  return { ...state, login, logout, hasRole };
}
