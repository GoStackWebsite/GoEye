"use client";

import { Card } from "../../components/Card";
import { usePolling } from "../../core/usePolling";
import { listZoneOccupancy } from "./api";
import styles from "./LineCounts.module.css";

const REFRESH_MS = 2_000;

export function ZoneOccupancy() {
  const { data: zones, error } = usePolling(listZoneOccupancy, REFRESH_MS);

  return (
    <Card title="People in zones now">
      {error && <p className={styles.error}>{error}</p>}
      {zones?.length === 0 && <p className={styles.muted}>No zones yet. Open Zones on a camera and draw one.</p>}
      <ul className={styles.list}>
        {zones?.map((zone) => (
          <li key={zone.id} className={styles.item}>
            <span className={styles.name}>
              {zone.name}
              <span className={styles.muted}> · {zone.camera_id}</span>
            </span>
            <span className={styles.count}>
              {zone.people ?? "–"} <span className={styles.label}>{zone.people === 1 ? "PERSON" : "PEOPLE"}</span>
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
