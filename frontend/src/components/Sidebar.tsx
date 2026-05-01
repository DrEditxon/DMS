"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Truck, 
  Users, 
  Settings, 
  LogOut,
  PackagePlus,
  Map as MapIcon
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const menuItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Entregas', href: '/deliveries', icon: Truck },
  { name: 'Mapa', href: '/map', icon: MapIcon }, // Asegúrate de importar MapIcon de lucide-react
  { name: 'Nueva Entrega', href: '/deliveries/new', icon: PackagePlus },
  { name: 'Usuarios', href: '/users', icon: Users },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen bg-slate-900 text-slate-300 flex flex-col fixed left-0 top-0 border-r border-slate-800">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">D</div>
          DMS
        </h1>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive 
                  ? "bg-blue-600/10 text-blue-400 font-medium" 
                  : "hover:bg-slate-800 hover:text-white"
              )}
            >
              <Icon className={cn(
                "w-5 h-5",
                isActive ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300"
              )} />
              {item.name}
              {isActive && <div className="ml-auto w-1.5 h-1.5 bg-blue-400 rounded-full" />}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto border-t border-slate-800">
        <button 
          onClick={() => {
            localStorage.removeItem('token');
            window.location.href = '/login';
          }}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-xl hover:bg-red-500/10 hover:text-red-400 transition-all text-slate-500"
        >
          <LogOut className="w-5 h-5" />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
}
