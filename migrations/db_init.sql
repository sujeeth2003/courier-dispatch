-- Plain SQL init script (used as an alternative to app-side create_all() for local psql access).
-- The FastAPI app also creates these tables on startup via SQLAlchemy metadata.create_all().

CREATE TYPE courier_status AS ENUM ('available', 'busy', 'offline');
CREATE TYPE order_status AS ENUM ('pending', 'assigned', 'picked_up', 'delivered', 'cancelled');

CREATE TABLE IF NOT EXISTS couriers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL DEFAULT 'Courier',
    status courier_status NOT NULL DEFAULT 'available',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pickup_lat DOUBLE PRECISION NOT NULL,
    pickup_lon DOUBLE PRECISION NOT NULL,
    dropoff_lat DOUBLE PRECISION NOT NULL,
    dropoff_lon DOUBLE PRECISION NOT NULL,
    status order_status NOT NULL DEFAULT 'pending',
    courier_id UUID REFERENCES couriers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    courier_id UUID NOT NULL REFERENCES couriers(id),
    pickup_distance_km DOUBLE PRECISION NOT NULL,
    strategy VARCHAR NOT NULL DEFAULT 'nearest',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
