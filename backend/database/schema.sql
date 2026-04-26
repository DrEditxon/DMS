-- ============================================================
--  DMS — Delivery Management System
--  Esquema completo de base de datos PostgreSQL
--  Optimizado para escalabilidad y producción
-- ============================================================

-- ── Extensiones ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID nativo
CREATE EXTENSION IF NOT EXISTS "postgis";      -- Coordenadas espaciales

-- ── ENUMs ────────────────────────────────────────────────────
CREATE TYPE user_role AS ENUM (
    'ADMIN',
    'DRIVER',
    'VIEWER'
);

CREATE TYPE delivery_status AS ENUM (
    'PENDING',      -- Creada, sin asignar
    'ASSIGNED',     -- Asignada a un repartidor
    'IN_TRANSIT',   -- En camino
    'DELIVERED',    -- Entregada exitosamente
    'FAILED',       -- Falló la entrega
    'CANCELLED'     -- Cancelada antes de iniciar
);

CREATE TYPE field_type AS ENUM (
    'TEXT',
    'NUMBER',
    'DATE',
    'BOOLEAN',
    'SELECT'        -- Lista de opciones definida en config
);

CREATE TYPE proof_type AS ENUM (
    'PHOTO',
    'SIGNATURE',
    'QR_CODE',
    'DOCUMENT'
);

-- ============================================================
--  TABLA: users
--  Usuarios del sistema: administradores, repartidores, viewers
-- ============================================================
CREATE TABLE users (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name       VARCHAR(150)    NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    phone           VARCHAR(30),
    password_hash   VARCHAR(255)    NOT NULL,
    role            user_role       NOT NULL DEFAULT 'DRIVER',
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    avatar_url      TEXT,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT users_email_unique UNIQUE (email)
);

-- Índices para users
CREATE INDEX idx_users_email       ON users (email);
CREATE INDEX idx_users_role        ON users (role);
CREATE INDEX idx_users_is_active   ON users (is_active) WHERE is_active = TRUE;

COMMENT ON TABLE  users               IS 'Usuarios del sistema DMS (admins, drivers, viewers)';
COMMENT ON COLUMN users.password_hash IS 'Hash bcrypt de la contraseña, nunca texto plano';
COMMENT ON COLUMN users.avatar_url    IS 'URL a imagen de perfil (S3, CDN, etc.)';

-- ============================================================
--  TABLA: deliveries
--  Entrega principal — corazón del sistema
-- ============================================================
CREATE TABLE deliveries (
    id               UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_no      VARCHAR(60)     NOT NULL,

    -- Asignación
    driver_id        UUID            REFERENCES users(id) ON DELETE SET NULL,
    created_by       UUID            NOT NULL REFERENCES users(id) ON DELETE RESTRICT,

    -- Estado
    status           delivery_status NOT NULL DEFAULT 'PENDING',

    -- Destinatario
    recipient_name   VARCHAR(150)    NOT NULL,
    recipient_phone  VARCHAR(30),
    recipient_email  VARCHAR(255),

    -- Dirección (desnormalizada para rendimiento + coords para mapa)
    address_street   VARCHAR(255)    NOT NULL,
    address_city     VARCHAR(100)    NOT NULL,
    address_state    VARCHAR(100),
    address_country  VARCHAR(100)    NOT NULL DEFAULT 'Colombia',
    address_zip      VARCHAR(20),
    location         GEOGRAPHY(POINT, 4326),   -- PostGIS: lat/lng

    -- Logística
    scheduled_at     TIMESTAMPTZ     NOT NULL,
    delivered_at     TIMESTAMPTZ,
    failed_at        TIMESTAMPTZ,
    failure_reason   TEXT,
    notes            TEXT,
    priority         SMALLINT        NOT NULL DEFAULT 3  -- 1=urgente, 5=baja
                     CHECK (priority BETWEEN 1 AND 5),

    -- Auditoría
    created_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT deliveries_tracking_unique UNIQUE (tracking_no)
);

-- Índices para deliveries
CREATE INDEX idx_deliveries_status        ON deliveries (status);
CREATE INDEX idx_deliveries_driver        ON deliveries (driver_id);
CREATE INDEX idx_deliveries_created_by    ON deliveries (created_by);
CREATE INDEX idx_deliveries_tracking      ON deliveries (tracking_no);
CREATE INDEX idx_deliveries_scheduled     ON deliveries (scheduled_at);
CREATE INDEX idx_deliveries_city          ON deliveries (address_city);
CREATE INDEX idx_deliveries_priority      ON deliveries (priority);
CREATE INDEX idx_deliveries_status_driver ON deliveries (status, driver_id);   -- compuesto
CREATE INDEX idx_deliveries_location      ON deliveries USING GIST (location); -- espacial

COMMENT ON TABLE  deliveries            IS 'Entregas principales del sistema';
COMMENT ON COLUMN deliveries.location   IS 'Coordenada PostGIS POINT(lng lat) SRID 4326';
COMMENT ON COLUMN deliveries.priority   IS '1=Urgente, 2=Alta, 3=Normal, 4=Baja, 5=Mínima';
COMMENT ON COLUMN deliveries.tracking_no IS 'Código único de seguimiento, visible al cliente';

-- ============================================================
--  TABLA: delivery_items
--  Ítems / productos incluidos en cada entrega
-- ============================================================
CREATE TABLE delivery_items (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    delivery_id     UUID            NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,

    -- Descripción del ítem
    name            VARCHAR(200)    NOT NULL,
    description     TEXT,
    sku             VARCHAR(100),
    quantity        NUMERIC(10, 2)  NOT NULL DEFAULT 1
                    CHECK (quantity > 0),
    unit            VARCHAR(30)     NOT NULL DEFAULT 'unidad',  -- kg, caja, unidad...
    weight_kg       NUMERIC(8, 3),
    declared_value  NUMERIC(12, 2),                            -- Para seguros
    requires_refrigeration BOOLEAN  NOT NULL DEFAULT FALSE,
    is_fragile      BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Índices para delivery_items
CREATE INDEX idx_items_delivery  ON delivery_items (delivery_id);
CREATE INDEX idx_items_sku       ON delivery_items (sku) WHERE sku IS NOT NULL;

COMMENT ON TABLE  delivery_items               IS 'Productos o ítems incluidos en una entrega';
COMMENT ON COLUMN delivery_items.declared_value IS 'Valor declarado del ítem (USD) para seguros o aduana';
COMMENT ON COLUMN delivery_items.unit           IS 'Unidad de medida: unidad, kg, caja, palet, etc.';

-- ============================================================
--  TABLA: delivery_proofs
--  Evidencias de entrega: fotos, firmas, QR, documentos
-- ============================================================
CREATE TABLE delivery_proofs (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    delivery_id     UUID            NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    uploaded_by     UUID            REFERENCES users(id) ON DELETE SET NULL,

    proof_type      proof_type      NOT NULL,
    file_url        TEXT            NOT NULL,       -- S3/CDN URL
    file_name       VARCHAR(255),
    mime_type       VARCHAR(100),
    file_size_bytes INTEGER,

    -- Contexto de captura
    captured_at     TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    capture_location GEOGRAPHY(POINT, 4326),        -- Dónde se tomó la foto
    notes           TEXT,

    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Índices para delivery_proofs
CREATE INDEX idx_proofs_delivery  ON delivery_proofs (delivery_id);
CREATE INDEX idx_proofs_type      ON delivery_proofs (proof_type);
CREATE INDEX idx_proofs_uploader  ON delivery_proofs (uploaded_by);

COMMENT ON TABLE  delivery_proofs                 IS 'Evidencias multimedia de entrega: fotos, firmas, QR';
COMMENT ON COLUMN delivery_proofs.capture_location IS 'GPS al momento de capturar la evidencia (PostGIS)';
COMMENT ON COLUMN delivery_proofs.file_url         IS 'URL pública o firmada del archivo en almacenamiento externo';

-- ============================================================
--  TABLA: custom_fields
--  Campos dinámicos configurables por administradores
--  Permite extender el formulario de entrega sin migraciones
-- ============================================================
CREATE TABLE custom_fields (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by      UUID            REFERENCES users(id) ON DELETE SET NULL,

    name            VARCHAR(100)    NOT NULL,    -- Nombre interno (snake_case)
    label           VARCHAR(150)    NOT NULL,    -- Etiqueta visible al usuario
    field_type      field_type      NOT NULL,
    is_required     BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    applies_to      VARCHAR(50)     NOT NULL DEFAULT 'delivery',  -- 'delivery' | 'item'
    sort_order      SMALLINT        NOT NULL DEFAULT 0,

    -- Para tipo SELECT: opciones en JSON ["Opción A","Opción B"]
    options         JSONB,

    -- Validaciones opcionales
    min_value       NUMERIC,
    max_value       NUMERIC,
    regex_pattern   TEXT,
    placeholder     VARCHAR(255),
    help_text       TEXT,

    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT custom_fields_name_entity_unique UNIQUE (name, applies_to)
);

-- Índices para custom_fields
CREATE INDEX idx_custom_fields_active    ON custom_fields (is_active) WHERE is_active = TRUE;
CREATE INDEX idx_custom_fields_applies   ON custom_fields (applies_to);
CREATE INDEX idx_custom_fields_sort      ON custom_fields (applies_to, sort_order);

COMMENT ON TABLE  custom_fields         IS 'Campos dinámicos configurables sin necesitar migraciones de esquema';
COMMENT ON COLUMN custom_fields.name    IS 'Identificador interno en snake_case. Único por applies_to';
COMMENT ON COLUMN custom_fields.options IS 'JSON array de opciones para tipo SELECT';
COMMENT ON COLUMN custom_fields.applies_to IS 'Entidad a la que aplica: ''delivery'' o ''item''';

-- ============================================================
--  TABLA: custom_field_values
--  Valores de los campos dinámicos por entrega o ítem
-- ============================================================
CREATE TABLE custom_field_values (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id        UUID            NOT NULL REFERENCES custom_fields(id) ON DELETE CASCADE,

    -- Una FK activa a la vez (delivery o item, no ambas)
    delivery_id     UUID            REFERENCES deliveries(id)      ON DELETE CASCADE,
    item_id         UUID            REFERENCES delivery_items(id)  ON DELETE CASCADE,

    value_text      TEXT,
    value_number    NUMERIC,
    value_date      TIMESTAMPTZ,
    value_boolean   BOOLEAN,

    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- Garantiza un solo valor por campo/entrega o campo/ítem
    CONSTRAINT cfv_delivery_unique UNIQUE (field_id, delivery_id),
    CONSTRAINT cfv_item_unique     UNIQUE (field_id, item_id),

    -- Solo uno de los dos puede ser no-nulo
    CONSTRAINT cfv_single_entity CHECK (
        (delivery_id IS NOT NULL AND item_id IS NULL) OR
        (item_id IS NOT NULL AND delivery_id IS NULL)
    )
);

-- Índices para custom_field_values
CREATE INDEX idx_cfv_delivery ON custom_field_values (delivery_id) WHERE delivery_id IS NOT NULL;
CREATE INDEX idx_cfv_item     ON custom_field_values (item_id)     WHERE item_id     IS NOT NULL;
CREATE INDEX idx_cfv_field    ON custom_field_values (field_id);

COMMENT ON TABLE  custom_field_values IS 'Valores EAV de los campos dinámicos por entrega o ítem';
COMMENT ON COLUMN custom_field_values.value_text    IS 'Valor para tipos TEXT y SELECT';
COMMENT ON COLUMN custom_field_values.value_number  IS 'Valor para tipo NUMBER';
COMMENT ON COLUMN custom_field_values.value_date    IS 'Valor para tipo DATE';
COMMENT ON COLUMN custom_field_values.value_boolean IS 'Valor para tipo BOOLEAN';

-- ============================================================
--  TRIGGER: updated_at automático en todas las tablas
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a cada tabla con updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'users', 'deliveries', 'delivery_items',
        'custom_fields', 'custom_field_values'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
            t, t
        );
    END LOOP;
END;
$$;

-- ============================================================
--  VISTA: v_delivery_summary
--  Vista desnormalizada para listados rápidos (evita JOINs en app)
-- ============================================================
CREATE OR REPLACE VIEW v_delivery_summary AS
SELECT
    d.id,
    d.tracking_no,
    d.status,
    d.priority,
    d.recipient_name,
    d.recipient_phone,
    d.address_city,
    d.address_country,
    d.scheduled_at,
    d.delivered_at,
    d.created_at,
    -- Repartidor
    u.id          AS driver_id,
    u.full_name   AS driver_name,
    u.phone       AS driver_phone,
    -- Agregados
    COUNT(DISTINCT di.id)  AS total_items,
    COUNT(DISTINCT dp.id)  AS total_proofs,
    ST_X(d.location::geometry) AS lng,
    ST_Y(d.location::geometry) AS lat
FROM deliveries d
LEFT JOIN users          u  ON u.id  = d.driver_id
LEFT JOIN delivery_items di ON di.delivery_id = d.id
LEFT JOIN delivery_proofs dp ON dp.delivery_id = d.id
GROUP BY d.id, u.id;

COMMENT ON VIEW v_delivery_summary IS 'Vista optimizada para listados del dashboard, evita N+1 en la app';

-- ============================================================
--  EJEMPLOS DE INSERCIÓN
-- ============================================================

-- 1. Usuarios
INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
    ('Carlos Admin',   'admin@dms.com',   '+57 301 000 0001', '$2b$12$examplehash1', 'ADMIN'),
    ('María Driver',   'driver@dms.com',  '+57 302 000 0002', '$2b$12$examplehash2', 'DRIVER'),
    ('Pedro Viewer',   'viewer@dms.com',  '+57 303 000 0003', '$2b$12$examplehash3', 'VIEWER');

-- 2. Campos personalizados
INSERT INTO custom_fields (name, label, field_type, is_required, applies_to, sort_order, options) VALUES
    ('order_source',  'Origen del pedido', 'SELECT',  TRUE,  'delivery', 1,
     '["Web","App Móvil","Teléfono","Tienda Física"]'::jsonb),
    ('cod_amount',    'Valor COD (COP)',   'NUMBER',  FALSE, 'delivery', 2, NULL),
    ('internal_notes','Notas internas',    'TEXT',    FALSE, 'delivery', 3, NULL),
    ('serial_number', 'Número de serie',  'TEXT',    FALSE, 'item',     1, NULL);

-- 3. Entrega completa
WITH admin AS (SELECT id FROM users WHERE email = 'admin@dms.com'),
     driver AS (SELECT id FROM users WHERE email = 'driver@dms.com')
INSERT INTO deliveries (
    tracking_no, driver_id, created_by,
    recipient_name, recipient_phone,
    address_street, address_city, address_country,
    location,
    scheduled_at, priority, notes
)
SELECT
    'TRK-2026-001',
    (SELECT id FROM driver),
    (SELECT id FROM admin),
    'Juan Pérez', '+57 310 111 2233',
    'Cra 7 # 32-16', 'Bogotá', 'Colombia',
    ST_SetSRID(ST_MakePoint(-74.0721, 4.7110), 4326),  -- lng, lat Bogotá
    NOW() + INTERVAL '2 hours', 2, 'Llamar antes de llegar'
FROM admin, driver;

-- 4. Ítems de la entrega
INSERT INTO delivery_items (delivery_id, name, sku, quantity, unit, weight_kg, declared_value, is_fragile)
SELECT
    d.id,
    'Laptop Dell XPS 13',
    'DELL-XPS13-2026',
    1, 'unidad', 1.25, 3500000, TRUE
FROM deliveries d WHERE d.tracking_no = 'TRK-2026-001';

INSERT INTO delivery_items (delivery_id, name, sku, quantity, unit, weight_kg)
SELECT
    d.id,
    'Mouse Inalámbrico',
    'MOUSE-WL-001',
    2, 'unidad', 0.15
FROM deliveries d WHERE d.tracking_no = 'TRK-2026-001';

-- 5. Valores de campos personalizados
INSERT INTO custom_field_values (field_id, delivery_id, value_text)
SELECT
    cf.id,
    d.id,
    'App Móvil'
FROM custom_fields cf, deliveries d
WHERE cf.name = 'order_source'
  AND d.tracking_no = 'TRK-2026-001';

INSERT INTO custom_field_values (field_id, delivery_id, value_number)
SELECT
    cf.id,
    d.id,
    150000  -- COP a cobrar
FROM custom_fields cf, deliveries d
WHERE cf.name = 'cod_amount'
  AND d.tracking_no = 'TRK-2026-001';

-- 6. Evidencia de entrega (simulada)
INSERT INTO delivery_proofs (delivery_id, uploaded_by, proof_type, file_url, mime_type, notes)
SELECT
    d.id,
    u.id,
    'PHOTO',
    'https://cdn.dms.com/proofs/TRK-2026-001/foto_firma.jpg',
    'image/jpeg',
    'Foto de firma del receptor'
FROM deliveries d, users u
WHERE d.tracking_no = 'TRK-2026-001'
  AND u.email = 'driver@dms.com';

-- 7. Actualizar estado de entrega
UPDATE deliveries
SET status = 'DELIVERED',
    delivered_at = NOW()
WHERE tracking_no = 'TRK-2026-001';

-- ============================================================
--  QUERIES DE VERIFICACIÓN
-- ============================================================

-- Ver resumen de la entrega
SELECT * FROM v_delivery_summary WHERE tracking_no = 'TRK-2026-001';

-- Entregas pendientes de un repartidor
SELECT d.tracking_no, d.recipient_name, d.address_city, d.scheduled_at
FROM deliveries d
JOIN users u ON u.id = d.driver_id
WHERE u.email = 'driver@dms.com'
  AND d.status IN ('ASSIGNED', 'IN_TRANSIT')
ORDER BY d.scheduled_at;

-- Conteo por estado (para dashboard)
SELECT status, COUNT(*) AS total
FROM deliveries
GROUP BY status
ORDER BY total DESC;

-- Entregas dentro de 5 km de un punto (PostGIS)
SELECT tracking_no, recipient_name,
       ST_Distance(location, ST_SetSRID(ST_MakePoint(-74.0721, 4.7110), 4326)) AS dist_meters
FROM deliveries
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(-74.0721, 4.7110), 4326),
    5000  -- metros
)
ORDER BY dist_meters;
