import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import { currentLearner, refreshSession, type Learner } from "./api";

const sessionKey = ["session"] as const;

export function useSession() {
  return useQuery({
    queryKey: sessionKey,
    queryFn: loadSession,
    retry: false,
    staleTime: 60_000,
  });
}

export function useRememberLearner() {
  const client = useQueryClient();
  return useCallback(
    (learner: Learner | null) => {
      client.setQueryData(sessionKey, learner);
    },
    [client],
  );
}

async function loadSession(): Promise<Learner | null> {
  const restored = await refreshSession();
  if (!restored) return null;
  return currentLearner();
}
