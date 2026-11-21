import styles from "./StatusBadge.module.css";

interface StatusBadgeProps {
  ok: boolean;
  label: string;
}

export function StatusBadge({ ok, label }: StatusBadgeProps) {
  return (
    <span className={styles.badge}>
      <span className={ok ? styles.dotOk : styles.dotBad} />
      {label}
    </span>
  );
}
