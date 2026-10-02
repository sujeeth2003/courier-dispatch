import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://courier:courier@localhost:5432/courier_dispatch_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
