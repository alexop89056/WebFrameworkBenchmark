# Web framework benchmark lab

Small Docker-based benchmark suite for comparing minimal `GET /` HTTP
handlers across frameworks, languages, and server configurations.

This repository is intended for experiments and reproducible local tests. It
is not a production benchmark and does not represent general framework
performance.

Suggested repository description: **Docker benchmark lab for minimal HTTP
handlers across web frameworks, languages, and server configurations.**

Suggested GitHub topics: `benchmark`, `docker`, `http`, `django`, `fastapi`,
`golang`, `rust`, `java`, `cpp`, `aspnet-core`.

## Layout

```text
.
├── services/            # One self-contained Docker build per implementation
├── docker-compose.yml   # Ports, CPU affinity, and worker configurations
├── benchmark.py         # Dependency-free benchmark runner
├── scripts/             # Smoke checks
├── Makefile             # Convenient local commands
├── docs/                # Notes and captured benchmark results
├── LICENSE
└── README.md
```

## Services

| Service | Endpoint |
|---|---|
| Django | `http://localhost:8101/` |
| FastAPI | `http://localhost:8102/` |
| Django-Bolt | `http://localhost:8103/` |
| Go Echo | `http://localhost:8104/` |
| Rust Axum | `http://localhost:8105/` |
| PHP native | `http://localhost:8106/` |
| Node native | `http://localhost:8107/` |
| Java native | `http://localhost:8108/` |
| Express | `http://localhost:8109/` |
| Fastify | `http://localhost:8110/` |
| ASP.NET Minimal API | `http://localhost:8111/` |
| C++ native | `http://localhost:8112/` |

Worker and server variants use ports `8113–8125`. See
[`docker-compose.yml`](docker-compose.yml) for the complete mapping.

## Run

Requirements:

- Docker Engine with Compose
- `wrk` for the long-running benchmark (the examples use its Docker image)
- Python 3.10+ for `benchmark.py`

Start only the baseline services:

```bash
docker compose --profile baseline up --build -d --wait
```

Start the worker/server variants:

```bash
docker compose --profile variants up --build -d --wait
```

Start both groups:

```bash
docker compose --profile baseline --profile variants up --build -d --wait
```

Check a service:

```bash
curl http://127.0.0.1:8104/
```

Run the dependency-free benchmark with warm-up, three repetitions, and
keep-alive connections:

```bash
python3 benchmark.py -n 1000 -c 200 -r 3 --warmup-requests 100 \
  --suite baseline \
  --json-out results/keepalive.json \
  --csv-out results/keepalive.csv \
  --docker-stats-out results/docker-stats.json
```

Test new TCP connections instead of keep-alive:

```bash
python3 benchmark.py -n 1000 -c 200 --connection-mode new
```

Use `--suite variants` for the worker/server profile or `--suite all` when
both Compose profiles are running.

The same workflows are available through the Makefile:

```bash
make smoke-baseline
make smoke-variants
make benchmark-all
make clean
```

Each service has a Docker healthcheck. The smoke test additionally validates
that `GET /` returns HTTP success and contains the standard `message: hello`
payload.

Run a keep-alive benchmark with 4 wrk threads and 200 connections:

```bash
docker run --rm --network host \
  williamyeh/wrk -t4 -c200 -d30s http://127.0.0.1:8104/
```

Stop and remove the Compose containers and network. Automatic restart is
disabled so crashes remain visible in `docker compose ps` and logs.

```bash
docker compose --profile baseline --profile variants down
```

## Interpreting results

`wrk` and `benchmark.py` measure different things. `wrk` reuses persistent
connections and is better suited to sustained HTTP throughput. The Python
script creates a new client connection per request, so its RPS is normally
lower and should not be compared directly with `wrk`.

Each baseline service has a dedicated CPU affinity in Compose. Worker variants
use CPUs `0–3`; this makes the experiments repeatable on the original test
machine, but it is not a universal hardware recommendation. For meaningful
comparisons, use the same machine, OS, Docker version, request body, client
settings, and warm-up period.

Captured results and caveats are in
[`docs/benchmark-results.md`](docs/benchmark-results.md).
