import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { Navigate } from "react-router-dom";

type AdminModeContextValue = {
  isAdminMode: boolean;
  setAdminMode: (nextValue: boolean) => void;
};

const ADMIN_MODE_STORAGE_KEY = "rag-admin-mode";
const AdminModeContext = createContext<AdminModeContextValue | null>(null);

function parseBoolean(value: string | undefined): boolean | null {
  if (!value) {
    return null;
  }
  const normalized = value.trim().toLowerCase();
  if (normalized === "true") {
    return true;
  }
  if (normalized === "false") {
    return false;
  }
  return null;
}

function getDefaultAdminMode(): boolean {
  const configuredDefault = parseBoolean(import.meta.env.VITE_ADMIN_MODE_DEFAULT);
  if (configuredDefault !== null) {
    return configuredDefault;
  }
  return import.meta.env.DEV;
}

function getInitialAdminMode(): boolean {
  const persistedValue = parseBoolean(window.localStorage.getItem(ADMIN_MODE_STORAGE_KEY) ?? undefined);
  if (persistedValue !== null) {
    return persistedValue;
  }
  return getDefaultAdminMode();
}

export function AdminModeProvider({ children }: { children: ReactNode }) {
  const [isAdminMode, setIsAdminMode] = useState<boolean>(getInitialAdminMode);

  const value = useMemo<AdminModeContextValue>(
    () => ({
      isAdminMode,
      setAdminMode: (nextValue) => {
        setIsAdminMode(nextValue);
        window.localStorage.setItem(ADMIN_MODE_STORAGE_KEY, String(nextValue));
      },
    }),
    [isAdminMode],
  );

  return <AdminModeContext.Provider value={value}>{children}</AdminModeContext.Provider>;
}

export function useAdminMode() {
  const ctx = useContext(AdminModeContext);
  if (!ctx) {
    throw new Error("useAdminMode must be used within AdminModeProvider");
  }
  return ctx;
}

export function AdminOnlyRoute({ children }: { children: ReactNode }) {
  const { isAdminMode } = useAdminMode();
  if (!isAdminMode) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}

