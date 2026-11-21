"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { LOGIN_PATH } from "../../core/api";
import { getToken } from "../../core/auth";

/** Renders children only when a login token exists; otherwise sends the user to the login page.
 *  The check runs in the browser because the token lives in localStorage, which the server cannot see. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    if (getToken()) setAllowed(true);
    else router.replace(LOGIN_PATH);
  }, [router]);

  return allowed ? children : null;
}
