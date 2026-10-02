# Load testing

This directory contains a [Locust](https://locust.io/) file that exercises the two
write-heavy endpoints: `POST /orders` and `POST /couriers/{id}/location`.

## Running

1. Start the stack: `docker compose up -d`
2. Seed a few couriers with locations so orders have something to match against (Locust
   users each create their own courier on start, so this is optional).
3. Run Locust:

```bash
cd loadtest
locust -f locustfile.py --host http://localhost:8000
```

Open http://localhost:8089, set the number of users and spawn rate, and start the test.
Locust reports p50/p99 latency live in the "Statistics" tab, and you can export a full
HTML report with `--html report.html`.

### Headless / scripted runs at a few fixed rates

```bash
# ~10 req/s
locust -f locustfile.py --host http://localhost:8000 --headless -u 20 -r 5 -t 2m --csv rate_10

# ~50 req/s
locust -f locustfile.py --host http://localhost:8000 --headless -u 100 -r 20 -t 2m --csv rate_50

# ~150 req/s
locust -f locustfile.py --host http://localhost:8000 --headless -u 300 -r 50 -t 2m --csv rate_150
```

Each run produces `rate_*_stats.csv` with p50/p95/p99 columns per endpoint.

## Results (template — fill in after running locally)

| Rate (approx req/s) | Users | p50 (ms) | p95 (ms) | p99 (ms) | Failures |
|---|---|---|---|---|---|
| 10  | 20  | TBD | TBD | TBD | TBD |
| 50  | 100 | TBD | TBD | TBD | TBD |
| 150 | 300 | TBD | TBD | TBD | TBD |

**Where p99 degrades:** TBD — based on a sample run, note the request rate at which
`POST /orders` p99 latency starts climbing sharply (this is usually where Postgres row
locking contention on the couriers table becomes the bottleneck, since assignment holds
a `FOR UPDATE SKIP LOCKED` transaction per order). Fill in with the request rate and
p99 value observed once you've run the load test above.
