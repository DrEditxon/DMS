'use client';

import { useEffect, useState } from 'react';
import { userService } from '../services/userService';
import { User, Shield, Phone, Mail, MoreVertical, Edit2, Trash } from 'lucide-react';

export default function UserTable() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await userService.getAll();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const roleColors: Record<string, string> = {
    ADMIN: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    OPERATOR: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    DRIVER: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    VIEWER: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-white/10 bg-white/5">
            <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Usuario</th>
            <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Rol</th>
            <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Contacto</th>
            <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Estado</th>
            <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {loading ? (
            <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">Cargando...</td></tr>
          ) : users.map((user) => (
            <tr key={user.id} className="hover:bg-white/5 transition-all">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold">
                    {user.full_name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-medium text-white">{user.full_name}</p>
                    <p className="text-xs text-gray-500">ID: {user.id.slice(0, 8)}</p>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${roleColors[user.role]}`}>
                  {user.role}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Mail className="w-3 h-3" /> {user.email}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Phone className="w-3 h-3" /> {user.phone || 'N/A'}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`} />
                  <span className="text-sm text-gray-300">{user.is_active ? 'Activo' : 'Inactivo'}</span>
                </div>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="p-2 hover:bg-white/10 rounded-lg text-gray-500 transition-all">
                  <MoreVertical className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
