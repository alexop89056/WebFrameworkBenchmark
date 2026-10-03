# Captured benchmark results

These are observations from the original local machine, not acceptance
criteria. The test machine had an Intel Core i5-12400F, Docker containers with
CPU affinity, and other unrelated workloads running on the host.

Command:

```bash
docker run --rm --network host \
  williamyeh/wrk -t4 -c200 -d30s http://127.0.0.1:PORT/
```

The repository benchmark also supports warm-up requests, repeated runs,
keep-alive/new-connection modes, JSON/CSV output, p95/p99 latency, and a
`docker stats --no-stream` snapshot. See the root README for the command.

## Worker experiments

| Implementation | Configuration | RPS | Average latency | Errors |
|---|---|---:|---:|---:|
| Django/Gunicorn | 4 sync workers | 2,996 | 67 ms | 0 |
| Django/Gunicorn | 4 workers × 4 gthread threads | 8,620 | 25.7 ms | 0 |
| Django/Uvicorn | 4 workers, uvloop + httptools | 2,857 | 70 ms | 0 |
| Go Echo | 1 worker | 60,307 | 3.42 ms | 0 |
| Go Echo | 4 serving workers | 113,806 | 1.99 ms | 0 |
| Rust Axum | 1 Tokio worker | 77,520 | 2.65 ms | 0 |
| Rust Axum | 4 Tokio workers | 132,661 | 1.54 ms | 0 |
| Java native | 1 executor | 4,811 | 41.5 ms | 0 |
| Java native | 4 executor workers | 4,783 | 41.7 ms | 0 |
| C++ native | 1 socket worker | 26,431 | 7.21 ms | 0 |
| C++ native | 4 socket workers | 36,484 | 4.94 ms | 0 |

The implementations are intentionally minimal but not byte-for-byte
identical. In particular, the C++ response closes the connection, while Go
and Rust keep connections alive. Treat the table as a record of this lab's
configuration, not as a language leaderboard.
