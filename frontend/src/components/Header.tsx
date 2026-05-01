import NotificationCenter from "./NotificationCenter";
import { Search } from 'lucide-react';

export default function Header() {
  return (
    <header className="h-16 flex items-center justify-between px-8 bg-white border-b border-slate-100 sticky top-0 z-10">
      <div className="relative w-96">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input 
          type="text" 
          placeholder="BÃºsqueda rÃ¡pida (Ctrl + K)"
          className="w-full pl-10 pr-4 py-2 bg-slate-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
        />
      </div>

      <div className="flex items-center gap-4">
        <NotificationCenter />
        <div className="h-8 w-[1px] bg-slate-100 mx-2" />
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-bold text-slate-900 leading-none">Admin User</p>
            <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider mt-1">Administrador</p>
          </div>
          <div className="w-10 h-10 bg-slate-200 rounded-full border-2 border-white shadow-sm" />
        </div>
      </div>
    </header>
  );
}

