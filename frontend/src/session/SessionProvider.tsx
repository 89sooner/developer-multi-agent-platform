import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

interface SessionState {
  bearerToken: string;
  language: string;
  lastRunId: string | null;
  setBearerToken: (token: string) => void;
  clearBearerToken: () => void;
  setLanguage: (language: string) => void;
  setLastRunId: (runId: string | null) => void;
}

const STORAGE_KEY = "developer-multi-agent-platform/session";

const SessionContext = createContext<SessionState | null>(null);

function loadSession() {
  if (typeof window === "undefined") {
    return { bearerToken: "", language: "ko", lastRunId: null as string | null };
  }
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { bearerToken: "", language: "ko", lastRunId: null as string | null };
    }
    const parsed = JSON.parse(raw) as { bearerToken?: string; language?: string; lastRunId?: string | null };
    return {
      bearerToken: parsed.bearerToken ?? "",
      language: parsed.language ?? "ko",
      lastRunId: parsed.lastRunId ?? null
    };
  } catch {
    return { bearerToken: "", language: "ko", lastRunId: null as string | null };
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState(loadSession);

  const setBearerToken = useCallback((token: string) => {
    setSession((current) => ({ ...current, bearerToken: token }));
  }, []);

  const clearBearerToken = useCallback(() => {
    setSession((current) => ({ ...current, bearerToken: "" }));
  }, []);

  const setLanguage = useCallback((language: string) => {
    setSession((current) => ({ ...current, language }));
  }, []);

  const setLastRunId = useCallback((runId: string | null) => {
    setSession((current) => ({ ...current, lastRunId: runId }));
  }, []);

  useEffect(() => {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }, [session]);

  const value = useMemo<SessionState>(
    () => ({
      bearerToken: session.bearerToken,
      language: session.language,
      lastRunId: session.lastRunId,
      setBearerToken,
      clearBearerToken,
      setLanguage,
      setLastRunId
    }),
    [session.bearerToken, session.language, session.lastRunId, setBearerToken, clearBearerToken, setLanguage, setLastRunId]
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return context;
}
