from prometheus_client import Counter, Gauge, Histogram

assignment_latency_seconds = Histogram(
    "assignment_latency_seconds", "Time to assign a courier to an order"
)
