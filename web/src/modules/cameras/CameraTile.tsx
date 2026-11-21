import { StatusBadge } from "../../components/StatusBadge";
import { streamUrl, type Camera } from "./api";
import styles from "./CameraTile.module.css";

export function CameraTile({ camera }: { camera: Camera }) {
  return (
    <figure className={styles.tile}>
      <div className={styles.view}>
        {camera.online ? (
          <img className={styles.video} src={streamUrl(camera.id)} alt={`Live view of ${camera.id}`} />
        ) : (
          <span className={styles.offline}>No signal</span>
        )}
      </div>
      <figcaption className={styles.caption}>
        {camera.id}
        <StatusBadge ok={camera.online} label={camera.online ? "Online" : "Offline"} />
      </figcaption>
    </figure>
  );
}
