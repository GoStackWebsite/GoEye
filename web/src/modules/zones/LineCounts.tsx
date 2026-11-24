"use client";

import { Card } from "../../components/Card";
import { usePolling } from "../../core/usePolling";
import { listLineCounts } from "./api";
import styles from "./LineCounts.module.css";

const REFRESH_MS = 5_000;

/** Counts since the start of today on this computer's clock; worked out on every refresh so it rolls over at midnight. */
function loadToday() {
  const midnight = new Date();
  midnight.setHours(0, 0, 0, 0);
  return listLineCounts(midnight);
}

export function LineCounts() {
  const { data: lines, error } = usePolling(loadToday, REFRESH_MS);

  return (
    <Card title="In / out today">
      {error && <p className={styles.error}>{error}</p>}
      {lines?.length === 0 && (
        <p className={styles.muted}>No count lines yet. Open Zones on a camera and draw one across its entrance.</p>
      )}
      <ul className={styles.list}>
        {lines?.map((line) => (
          <li key={line.id} className={styles.item}>
            <span className={styles.name}>
              {line.name}
              <span className={styles.muted}> · {line.camera_id}</span>
            </span>
            <span className={styles.count}>
              <span className={styles.label}>IN</span> {line.entered}
            </span>
            <span className={styles.count}>
              <span className={styles.label}>OUT</span> {line.left}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
