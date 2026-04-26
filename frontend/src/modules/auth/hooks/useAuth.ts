"use client";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import api from "@/lib/api";
import type { TokenResponse } from "@/types";

export function useAuth() {
  const router = useRouter();
  const { setAuth, logout: storeLogout, user, isAuthenticated } = useAuthStore();

  const login = async (email: string, password: string) => {
    const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
    // Obtener datos del usuario
    localStorage.setItem("access_token", data.access_token);
    const meRes = await api.get("/users/me");
    setAuth(meRes.data, data.access_token, data.refresh_token);
    router.push("/dashboard");
  };

  const logout = () => {
    storeLogout();
    router.push("/login");
  };

  return { login, logout, user, isAuthenticated };
}
