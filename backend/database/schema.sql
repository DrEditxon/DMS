-- 1. Extensiones y Tipos ENUM
CREATE TYPE delivery_status AS ENUM (
    'pending',      -- Pendiente de asignación
    'assigned',     -- Asignado a conductor
    'picked_up',    -- Recogido / Iniciado
    'in_transit',   -- En camino
    'delivered',    -- Entregado con éxito
    'failed',       -- Intento fallido
    'cancelled'     -- Cancelado
);

CREATE TYPE user_role AS ENUM ('admin', 'dispatcher', 'driver');

-- 2. Tabla de Perfiles (Extensión de auth.users de Supabase)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    role user_role DEFAULT 'driver',
    phone TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Tabla de Entregas (Deliveries)
CREATE TABLE public.deliveries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tracking_number TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    status delivery_status DEFAULT 'pending',
    driver_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    dispatcher_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    scheduled_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Tabla de Ítems de Entrega (Delivery Items)
CREATE TABLE public.delivery_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    delivery_id UUID REFERENCES public.deliveries(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    weight_kg DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Pruebas de Entrega (Delivery Proofs)
CREATE TABLE public.delivery_proofs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    delivery_id UUID REFERENCES public.deliveries(id) ON DELETE CASCADE,
    proof_type TEXT CHECK (proof_type IN ('signature', 'photo', 'id_card')),
    media_url TEXT NOT NULL, -- URL de Supabase Storage
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Campos Personalizados (Custom Fields - para extensibilidad SaaS)
CREATE TABLE public.custom_fields (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    label TEXT NOT NULL,
    data_type TEXT CHECK (data_type IN ('text', 'number', 'boolean', 'date')),
    target_table TEXT CHECK (target_table IN ('deliveries', 'profiles')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE public.custom_field_values (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_id UUID REFERENCES public.custom_fields(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL, -- ID de la entrega o usuario
    value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(field_id, entity_id)
);

-- 7. Índices para Optimización
CREATE INDEX idx_deliveries_status ON public.deliveries(status);
CREATE INDEX idx_deliveries_driver ON public.deliveries(driver_id);
CREATE INDEX idx_deliveries_scheduled ON public.deliveries(scheduled_at);
CREATE INDEX idx_delivery_items_delivery ON public.delivery_items(delivery_id);
CREATE INDEX idx_custom_values_entity ON public.custom_field_values(entity_id);

-- 8. Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_modtime BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_deliveries_modtime BEFORE UPDATE ON public.deliveries FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_custom_values_modtime BEFORE UPDATE ON public.custom_field_values FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- 9. Ejemplos de Inserción
/*
-- Insertar un campo personalizado
INSERT INTO custom_fields (name, label, data_type, target_table) 
VALUES ('fragile_notes', 'Notas de Fragilidad', 'text', 'deliveries');

-- Crear una entrega básica
INSERT INTO deliveries (tracking_number, customer_name, address, status)
VALUES ('DMS-1001', 'Juan Pérez', 'Calle Falsa 123, Madrid', 'pending');
*/
