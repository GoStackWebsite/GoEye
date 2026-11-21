// Next.js inlines NEXT_PUBLIC_* at build time, so the variable must be referenced by its full name here.
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
if (!apiUrl) {
  throw new Error("NEXT_PUBLIC_API_URL is not set: copy web/.env.example to web/.env");
}

export const API_URL: string = apiUrl.replace(/\/$/, "");
