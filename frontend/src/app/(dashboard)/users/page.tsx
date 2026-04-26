"use client";
import useSWR from "swr";
import api from "@/lib/api";
import type { User } from "@/types";
import { getRoleLabel, formatDate } from "@/lib/utils";
import { Plus, UserCheck, UserX, Shield, Truck, Eye } from "lucide-react";
import { useState } from "react";

const fetcher = (url: string) => api.get(url).then((r) => r.data);

const ROLE_ICONS: Record<string, React.ElementType> = {
  ADMIN:  Shield,
  DRIVER: Truck,
  VIEWER: Eye,
};

function RoleBadge({ role }: { role: string }) {
  const Icon = ROLE_ICONS[role] ?? Eye;
  return (
    <span className={`badge badge-${role.toLowerCase()} gap-1`}>
      <Icon className="w-3 h-3" />
      {getRoleLabel(role)}
    </span>
  );
}

export default function UsersPage() {
  const { data: users, isLoading } = useSWR<User[]>("/users", fetcher);
  const [roleFilter, setRoleFilter] = useState("");

  const filtered = (users ?? []).filter((u) => !roleFilter || u.role === roleFilter);

  return (
    <div>
      <div className="page-header flex items-start justify-between">
        <div>
          <h1 className="page-title">Usuarios</h1>
          <p className="page-subtitle">
            {users ? `${users.length} usuario(s) registrados` : "Cargando..."}
          </p>
        </div>
        <button id="btn-new-user" className="btn-primary">
          <Plus className="w-4 h-4" />
          Nuevo usuario
        </button>
      </div>

      {/* Filter */}
      <div className="mb-6 flex gap-3">
        {["", "ADMIN", "DRIVER", "VIEWER"].map((r) => (
          <button
            key={r}
            id={`filter-role-${r || "all"}`}
            onClick={() => setRoleFilter(r)}
            className={`btn-sm ${roleFilter === r ? "btn-primary" : "btn-secondary"}`}
          >
            {r ? getRoleLabel(r) : "Todos"}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="table-container animate-fade-in">
        <table className="table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Registrado</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && Array.from({ length: 5 }).map((_, i) => (
              <tr key={i}>
                {Array.from({ length: 6 }).map((_, j) => (
                  <td key={j}><div className="skeleton h-4 rounded" /></td>
                ))}
              </tr>
            ))}
            {!isLoading && filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-12 text-slate-500">
                  No hay usuarios con este filtro
                </td>
              </tr>
            )}
            {filtered.map((user) => (
              <tr key={user.id} className="animate-fade-in">
                <td>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary-600/20 border border-primary-500/30 flex items-center justify-center text-primary-300 text-xs font-bold">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <span className="font-medium text-white">{user.full_name}</span>
                  </div>
                </td>
                <td className="text-slate-400 text-sm">{user.email}</td>
                <td className="text-slate-400 text-sm">{user.phone ?? "—"}</td>
                <td><RoleBadge role={user.role} /></td>
                <td>
                  {user.is_active
                    ? <span className="flex items-center gap-1 text-green-400 text-xs">
                        <UserCheck className="w-3.5 h-3.5" /> Activo
                      </span>
                    : <span className="flex items-center gap-1 text-red-400 text-xs">
                        <UserX className="w-3.5 h-3.5" /> Inactivo
                      </span>
                  }
                </td>
                <td className="text-slate-500 text-xs">{formatDate(user.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
