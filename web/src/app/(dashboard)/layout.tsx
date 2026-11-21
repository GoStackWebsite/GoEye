"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { LOGIN_PATH } from "../../core/api";
import { clearToken } from "../../core/auth";
import { RequireAuth } from "../../modules/auth/RequireAuth";
import styles from "./layout.module.css";

const NAV_ITEMS = [{ href: "/", label: "Dashboard" }];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const signOut = () => {
    clearToken();
    router.replace(LOGIN_PATH);
  };

  return (
    <RequireAuth>
      <header className={styles.bar}>
        <span className={styles.brand}>GoEye</span>
        <nav className={styles.nav}>
          {NAV_ITEMS.map(({ href, label }) => (
            <Link key={href} href={href} className={pathname === href ? styles.active : styles.link}>
              {label}
            </Link>
          ))}
        </nav>
        <button className={styles.signOut} onClick={signOut}>
          Sign out
        </button>
      </header>
      <main className={styles.main}>{children}</main>
    </RequireAuth>
  );
}
