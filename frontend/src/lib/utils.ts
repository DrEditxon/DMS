import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date));
}

export function formatDateShort(date: string | Date): string {
  return new Intl.DateTimeFormat("es-CO", { dateStyle: "short" }).format(new Date(date));
}

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    PENDING:    "Pendiente",
    ASSIGNED:   "Asignado",
    IN_TRANSIT: "En tránsito",
    DELIVERED:  "Entregado",
    FAILED:     "Fallido",
  };
  return labels[status] ?? status;
}

export function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    ADMIN:  "Administrador",
    DRIVER: "Repartidor",
    VIEWER: "Visualizador",
  };
  return labels[role] ?? role;
}
