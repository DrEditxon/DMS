"use client";

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Users, UserCog, Shield, ShieldCheck, Mail, Trash2 } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';

export default function UsersPage() {
  const queryClient = useQueryClient();

  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await api.get('/users');
      return res.data;
    }
  });

  const updateRole = useMutation({
    mutationFn: ({ id, role }: { id: str, role: str }) => 
      api.patch(`/users/${id}`, { role }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] })
  });

  const getRoleBadge = (role: str) => {
    switch (role) {
      case 'admin': return <span className="flex items-center gap-1.5 text-purple-700 bg-purple-100 px-2.5 py-1 rounded-full text-xs font-bold uppercase"><ShieldCheck className="w-3 h-3" /> Admin</span>;
      case 'operator': return <span className="flex items-center gap-1.5 text-blue-700 bg-blue-100 px-2.5 py-1 rounded-full text-xs font-bold uppercase"><Shield className="w-3 h-3" /> Operador</span>;
      default: return <span className="flex items-center gap-1.5 text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full text-xs font-bold uppercase">Conductor</span>;
    }
  };

  return (
    <div className="flex bg-slate-50 min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="p-8 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Gestión de Usuarios</h1>
              <p className="text-slate-500">Administra roles y permisos del personal de logística.</p>
            </div>
            <button className="px-6 py-2.5 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg">
              + Invitar Usuario
            </button>
          </div>

          <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider font-bold">
                  <th className="px-6 py-5">Usuario</th>
                  <th className="px-6 py-5">Rol Actual</th>
                  <th className="px-6 py-5">Estado</th>
                  <th className="px-6 py-5 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {isLoading ? (
                   Array.from({ length: 3 }).map((_, i) => (
                    <tr key={i} className="animate-pulse h-20 bg-slate-50/20" />
                  ))
                ) : (
                  users?.map((user: any) => (
                    <tr key={user.id} className="hover:bg-slate-50/50 transition-all group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-400">
                            {user.full_name?.charAt(0)}
                          </div>
                          <div>
                            <p className="text-sm font-bold text-slate-900">{user.full_name}</p>
                            <p className="text-xs text-slate-400 flex items-center gap-1"><Mail className="w-3 h-3" /> {user.email || 'sin-email@dms.com'}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <select 
                          value={user.role}
                          onChange={(e) => updateRole.mutate({ id: user.id, role: e.target.value })}
                          className="text-xs font-bold border-none bg-transparent focus:ring-0 cursor-pointer hover:text-blue-600 transition-colors"
                        >
                          <option value="admin">Administrador</option>
                          <option value="operator">Operador</option>
                          <option value="driver">Conductor</option>
                        </select>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1.5 text-emerald-600 font-bold text-xs">
                          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" /> Activo
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all">
                            <UserCog className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}
