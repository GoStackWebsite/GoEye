"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StatusBadge } from "../../components/StatusBadge";
import { streamUrl, type Camera } from "./api";
import styles from "./CameraTile.module.css";

export function CameraTile({ camera }: { camera: Camera }) {
  const [enlarged, setEnlarged] = useState(false);
  const showLarge = enlarged && camera.online;

  useEffect(() => {
    if (!showLarge) return;
    const closeOnEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") setEnlarged(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [showLarge]);

  return (
    <figure className={styles.tile}>
      {/* the same picture fills the window when enlarged, so no second stream is opened */}
      <div
        className={showLarge ? styles.viewLarge : styles.view}
        onClick={() => setEnlarged(camera.online && !showLarge)}
        title={showLarge ? "Click or press Esc to close" : undefined}
      >
        {camera.online ? (
          <img className={styles.video} src={streamUrl(camera.id)} alt={`Live view of ${camera.id}`} />
        ) : (
          <span className={styles.offline}>No signal</span>
        )}
      </div>
      <figcaption className={styles.caption}>
        {camera.id}
        <span className={styles.actions}>
          <button className={styles.link} onClick={() => setEnlarged(true)} disabled={!camera.online}>
            Enlarge
          </button>
          <Link className={styles.link} href={`/cameras/${encodeURIComponent(camera.id)}`}>
            Zones
          </Link>
          <StatusBadge ok={camera.online} label={camera.online ? "Online" : "Offline"} />
        </span>
      </figcaption>
    </figure>
  );
}
