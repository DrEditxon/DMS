from app.core.supabase import supabase
from datetime import datetime, timedelta

class StatsRepository:
    def get_dashboard_stats(self):
        # 1. Conteos por estado
        # Nota: En un sistema grande usaríamos una sola query con group by
        # Por ahora lo hacemos simple con Supabase
        total = supabase.table("deliveries").select("id", count="exact").execute().count
        completed = supabase.table("deliveries").select("id", count="exact").eq("status", "delivered").execute().count
        pending = supabase.table("deliveries").select("id", count="exact").eq("status", "pending").execute().count
        in_progress = supabase.table("deliveries").select("id", count="exact").eq("status", "in_transit").execute().count
        
        # 2. Datos para gráfico (últimos 7 días)
        # Simulado por brevedad, en prod se usaría una vista de postgres o rpc
        history = [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "count": 5 + i}
            for i in range(7)
        ]
        
        return {
            "total": total or 0,
            "completed": completed or 0,
            "pending": pending or 0,
            "in_progress": in_progress or 0,
            "history": history[::-1]
        }

stats_repo = StatsRepository()
