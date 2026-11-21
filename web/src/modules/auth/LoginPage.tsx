"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ApiError } from "../../core/api";
import { setToken } from "../../core/auth";
import { login } from "./api";
import styles from "./LoginPage.module.css";

export function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { access_token } = await login(email, password);
      setToken(access_token);
      router.replace("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unexpected error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className={styles.page}>
      <form className={styles.form} onSubmit={submit}>
        <h1 className={styles.title}>GoEye</h1>
        <label className={styles.field}>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
        </label>
        <label className={styles.field}>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <p className={styles.error}>{error}</p>}
        <button className={styles.submit} type="submit" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
