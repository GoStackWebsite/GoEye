"use client";

import { useCallback } from "react";
import { Card } from "../../components/Card";
import { usePolling } from "../../core/usePolling";
import { listRecentEvents } from "./api";
import styles from "./RecentEvents.module.css";

const EVENT_LIMIT = 20;
const REFRESH_MS = 10_000;

export function RecentEvents() {
  const load = useCallback(() => listRecentEvents(EVENT_LIMIT), []);
  const { data: events, error } = usePolling(load, REFRESH_MS);

  return (
    <Card title="Recent events">
      {error && <p className={styles.error}>{error}</p>}
      {events?.length === 0 && <p className={styles.muted}>No events yet</p>}
      <ul className={styles.list}>
        {events?.map((e) => (
          <li key={e.id} className={styles.item}>
            <span className={styles.type}>{e.type.replace("_", " ")}</span>
            <span className={styles.muted}>
              {e.camera_id}
              {e.zone_id && ` · ${e.zone_id}`}
            </span>
            <time className={styles.muted}>{new Date(e.ts).toLocaleTimeString()}</time>
          </li>
        ))}
      </ul>
    </Card>
  );
}
