from prometheus_client import Counter, Gauge, Histogram

assignment_latency_seconds = Histogram(
    "assignment_latency_seconds", "Time to assign a courier to an order"
)

pending_orders_gauge = Gauge(
    "pending_orders", "Number of orders currently unassigned"
)

orders_created_total = Counter(
    "orders_created_total", "Total number of orders created"
)

location_updates_total = Counter(
    "location_updates_total", "Total number of courier location updates"
)

assignments_total = Counter(
    "assignments_total", "Total number of successful assignments", ["strategy"]
)
