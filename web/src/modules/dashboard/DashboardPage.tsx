"use client";

import { Card } from "../../components/Card";
import { StatTile } from "../../components/StatTile";
import { StatusBadge } from "../../components/StatusBadge";
import { usePolling } from "../../core/usePolling";
import { listCameras } from "../cameras/api";
import { CameraTile } from "../cameras/CameraTile";
import { RecentEvents } from "../events/RecentEvents";
import { LineCounts } from "../zones/LineCounts";
import { ZoneOccupancy } from "../zones/ZoneOccupancy";
import styles from "./DashboardPage.module.css";

const CAMERA_REFRESH_MS = 5_000;
const NEEDS_DETECTION = "available once person detection runs";

export function DashboardPage() {
  const { data: cameras, error } = usePolling(listCameras, CAMERA_REFRESH_MS);
  const online = cameras?.filter((c) => c.online).length ?? 0;

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <StatusBadge ok={cameras !== null && online > 0} label={`${online}/${cameras?.length ?? 0} cameras online`} />
      </div>

      <div className={styles.tiles}>
        <StatTile label="People in view" value="–" hint={NEEDS_DETECTION} />
        <StatTile label="Staff on floor" value="–" hint={NEEDS_DETECTION} />
        <StatTile label="In queue now" value="–" hint={NEEDS_DETECTION} />
        <StatTile label="Avg dwell today" value="–" hint={NEEDS_DETECTION} />
      </div>

      <Card title="Cameras">
        {error && <p className={styles.error}>{error}</p>}
        {cameras?.length === 0 && <p className={styles.muted}>No cameras configured. Add them to CAMERAS in .env.</p>}
        <div className={styles.cameras}>
          {cameras?.map((camera) => <CameraTile key={camera.id} camera={camera} />)}
        </div>
      </Card>

      <ZoneOccupancy />

      <LineCounts />

      <RecentEvents />
    </div>
  );
}
