import type { ReactNode } from "react";
import styles from "./Card.module.css";

interface CardProps {
  title: string;
  aside?: ReactNode;
  children: ReactNode;
}

export function Card({ title, aside, children }: CardProps) {
  return (
    <section className={styles.card}>
      <header className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        {aside}
      </header>
      {children}
    </section>
  );
}
