import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DMS — Delivery Management System",
  description: "Sistema de gestión de entregas en tiempo real. Monitorea, asigna y rastrea tus entregas.",
};

import Providers from "@/components/Providers";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="bg-surface-900 text-slate-100 font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
