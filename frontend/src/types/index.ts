// Tipos globales TypeScript para el DMS

export type UserRole = "ADMIN" | "DRIVER" | "VIEWER";

export type DeliveryStatus = "PENDING" | "ASSIGNED" | "IN_TRANSIT" | "DELIVERED" | "FAILED";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Address {
  id: string;
  street: string;
  city: string;
  state?: string;
  country: string;
  postal_code?: string;
  lat?: number;
  lng?: number;
}

export interface Delivery {
  id: string;
  tracking_no: string;
  status: DeliveryStatus;
  recipient_name: string;
  recipient_phone?: string;
  scheduled_at: string;
  delivered_at?: string;
  notes?: string;
  driver?: User;
  address?: Address;
  created_at: string;
  updated_at?: string;
}

export interface DeliveryPage {
  items: Delivery[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DashboardStats {
  total_deliveries: number;
  pending: number;
  assigned: number;
  in_transit: number;
  delivered: number;
  failed: number;
  delivered_today: number;
  total_drivers: number;
  active_drivers: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
