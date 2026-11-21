"use client";

import { useEffect, useState } from "react";
import { ApiError } from "./api";

export interface PollingState<T> {
  data: T | null;
  error: string | null;
}

/** Load data now and again every intervalMs; keeps the last good data while showing the latest error. */
export function usePolling<T>(load: () => Promise<T>, intervalMs: number): PollingState<T> {
  const [state, setState] = useState<PollingState<T>>({ data: null, error: null });

  useEffect(() => {
    let active = true;
    const run = () =>
      load()
        .then((data) => active && setState({ data, error: null }))
        .catch((e: unknown) => {
          const message = e instanceof ApiError ? e.message : "Unexpected error";
          if (active) setState((prev) => ({ data: prev.data, error: message }));
        });
    run();
    const timer = window.setInterval(run, intervalMs);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [load, intervalMs]);

  return state;
}
