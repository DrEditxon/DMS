'use client';

import { Bell, Search, User } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="h-16 border-b border-white/5 bg-surface-900/50 backdrop-blur-xl sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="relative w-96 hidden md:block">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input 
          type="text" 
          placeholder="Buscar..." 
          className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        />
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full border-2 border-surface-900"></span>
        </button>
        
        <div className="h-8 w-px bg-white/5 mx-2"></div>

        <div className="flex items-center gap-3 pl-2 cursor-pointer group">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors">Admin User</p>
            <p className="text-[10px] text-gray-500 uppercase tracking-widest">Administrador</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center border-2 border-white/10">
            <User className="text-white w-5 h-5" />
          </div>
        </div>
      </div>
    </header>
  );
}
