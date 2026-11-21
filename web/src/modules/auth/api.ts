import { apiRequest } from "../../core/api";

interface TokenOut {
  access_token: string;
  token_type: string;
}

export function login(email: string, password: string): Promise<TokenOut> {
  return apiRequest<TokenOut>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
