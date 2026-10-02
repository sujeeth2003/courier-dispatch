from prometheus_client import Counter, Gauge, Histogram

assignment_latency_seconds = Histogram(
    "assignment_latency_seconds", "Time to assign a courier to an order"
)

pending_orders_gauge = Gauge(
    "pending_orders", "Number of orders currently unassigned"
)
