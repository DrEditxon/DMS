"use client";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import api from "@/lib/api";
import { ArrowLeft, Loader2, Package } from "lucide-react";
import { useState } from "react";

const schema = z.object({
  tracking_no:     z.string().min(3, "Mínimo 3 caracteres"),
  recipient_name:  z.string().min(2, "Nombre requerido"),
  recipient_phone: z.string().optional(),
  scheduled_at:    z.string().min(1, "Fecha requerida"),
  notes:           z.string().optional(),
  street:          z.string().min(3, "Calle requerida"),
  city:            z.string().min(2, "Ciudad requerida"),
  country:         z.string().default("Colombia"),
});

type FormData = z.infer<typeof schema>;

export default function NewDeliveryPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { country: "Colombia" },
  });

  const onSubmit = async (data: FormData) => {
    setError(null);
    try {
      await api.post("/deliveries", {
        tracking_no:     data.tracking_no,
        recipient_name:  data.recipient_name,
        recipient_phone: data.recipient_phone,
        scheduled_at:    data.scheduled_at,
        notes:           data.notes,
        address: {
          street:  data.street,
          city:    data.city,
          country: data.country,
        },
      });
      router.push("/deliveries");
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      setError(err.response?.data?.detail || "Error al crear la entrega");
    }
  };

  const Field = ({ id, label, error, children }: {
    id: string; label: string; error?: string; children: React.ReactNode;
  }) => (
    <div>
      <label className="label" htmlFor={id}>{label}</label>
      {children}
      {error && <p className="text-red-400 text-xs mt-1">{error}</p>}
    </div>
  );

  return (
    <div className="max-w-2xl">
      <div className="page-header flex items-center gap-4">
        <button id="btn-back" onClick={() => router.back()} className="btn-secondary btn-sm">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="page-title">Nueva Entrega</h1>
          <p className="page-subtitle">Registrar una nueva entrega en el sistema</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        <div className="card space-y-4">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <Package className="w-4 h-4 text-primary-400" />
            Información del paquete
          </h2>
          <Field id="tracking_no" label="Número de tracking" error={errors.tracking_no?.message}>
            <input id="tracking_no" className="input" placeholder="TRK-001" {...register("tracking_no")} />
          </Field>
          <Field id="scheduled_at" label="Fecha programada" error={errors.scheduled_at?.message}>
            <input id="scheduled_at" type="datetime-local" className="input" {...register("scheduled_at")} />
          </Field>
          <Field id="notes" label="Notas (opcional)">
            <textarea id="notes" className="input resize-none" rows={3} placeholder="Instrucciones especiales..." {...register("notes")} />
          </Field>
        </div>

        <div className="card space-y-4">
          <h2 className="font-semibold text-white">Destinatario</h2>
          <Field id="recipient_name" label="Nombre" error={errors.recipient_name?.message}>
            <input id="recipient_name" className="input" placeholder="Juan Pérez" {...register("recipient_name")} />
          </Field>
          <Field id="recipient_phone" label="Teléfono (opcional)">
            <input id="recipient_phone" className="input" placeholder="+57 300 000 0000" {...register("recipient_phone")} />
          </Field>
        </div>

        <div className="card space-y-4">
          <h2 className="font-semibold text-white">Dirección de entrega</h2>
          <Field id="street" label="Calle / Dirección" error={errors.street?.message}>
            <input id="street" className="input" placeholder="Calle 123 #45-67" {...register("street")} />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field id="city" label="Ciudad" error={errors.city?.message}>
              <input id="city" className="input" placeholder="Bogotá" {...register("city")} />
            </Field>
            <Field id="country" label="País">
              <input id="country" className="input" {...register("country")} />
            </Field>
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <button type="button" onClick={() => router.back()} className="btn-secondary">Cancelar</button>
          <button type="submit" id="btn-submit-delivery" disabled={isSubmitting} className="btn-primary">
            {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {isSubmitting ? "Creando..." : "Crear entrega"}
          </button>
        </div>
      </form>
    </div>
  );
}
