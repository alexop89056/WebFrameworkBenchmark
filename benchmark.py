#!/usr/bin/env python3
"""Small, dependency-free HTTP benchmark for the local containers."""

import argparse
import csv
import datetime as dt
import http.client
import json
import math
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


thread_state = threading.local()


def request(port, connection_mode):
    started = time.perf_counter()
    connection = None
    try:
        if connection_mode == "keepalive":
            connections = getattr(thread_state, "connections", {})
            thread_state.connections = connections
            connection = connections.get(port)
            if connection is None:
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                connections[port] = connection
        else:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=10)

        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read()
        status = response.status
        valid = status == 200 and b"hello" in body and b"message" in body

        if connection_mode == "new":
            connection.close()
        elapsed = (time.perf_counter() - started) * 1000
        return valid, status, elapsed
    except (OSError, http.client.HTTPException):
        if connection_mode == "keepalive":
            connections = getattr(thread_state, "connections", {})
            failed = connections.pop(port, None)
            if failed is not None:
                failed.close()
        elif connection is not None:
            connection.close()
        elapsed = (time.perf_counter() - started) * 1000
        return False, 0, elapsed


def run_batch(port, requests, concurrency, connection_mode):
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(
            pool.map(
                lambda _: request(port, connection_mode),
                range(requests),
            )
        )
    elapsed = time.perf_counter() - started
    return results, elapsed


def percentile(values, fraction):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def run_target(target, args):
    name, port = target
    if args.warmup_requests:
        run_batch(port, args.warmup_requests, args.concurrency, args.connection_mode)

    all_latencies = []
    total_elapsed = 0.0
    total_requests = 0
    errors = 0
    status_counts = {}

    for _ in range(args.repeats):
        results, elapsed = run_batch(
            port, args.requests, args.concurrency, args.connection_mode
        )
        total_elapsed += elapsed
        total_requests += len(results)
        for valid, status, latency in results:
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1
            if valid:
                all_latencies.append(latency)
            else:
                errors += 1

    return {
        "server": name,
        "port": port,
        "connection_mode": args.connection_mode,
        "requests_per_repeat": args.requests,
        "repeats": args.repeats,
        "warmup_requests": args.warmup_requests,
        "concurrency": args.concurrency,
        "requests": total_requests,
        "successful": len(all_latencies),
        "errors": errors,
        "status_counts": status_counts,
        "rps": len(all_latencies) / max(total_elapsed, 0.000001),
        "avg_ms": statistics.mean(all_latencies) if all_latencies else 0.0,
        "median_ms": statistics.median(all_latencies) if all_latencies else 0.0,
        "p95_ms": percentile(all_latencies, 0.95),
        "p99_ms": percentile(all_latencies, 0.99),
    }


def collect_docker_stats():
    command = [
        "docker",
        "stats",
        "--no-stream",
        "--format",
        "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}",
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"warning: docker stats unavailable: {exc}", file=sys.stderr)
        return []

    rows = []
    for line in completed.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 6:
            rows.append(
                {
                    "name": parts[0],
                    "cpu_percent": parts[1],
                    "memory": parts[2],
                    "network_io": parts[3],
                    "block_io": parts[4],
                    "pids": parts[5],
                }
            )
    return rows


def write_results(results, args):
    if args.json_out:
        payload = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "settings": {
                "requests": args.requests,
                "repeats": args.repeats,
                "concurrency": args.concurrency,
                "warmup_requests": args.warmup_requests,
                "connection_mode": args.connection_mode,
            },
            "results": results,
        }
        path = Path(args.json_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.csv_out:
        path = Path(args.csv_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "server", "port", "connection_mode", "requests", "successful",
            "errors", "rps", "avg_ms", "median_ms", "p95_ms", "p99_ms",
        ]
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows({field: result[field] for field in fields} for result in results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--requests", type=int, default=1000)
    parser.add_argument("-c", "--concurrency", type=int, default=200)
    parser.add_argument("-r", "--repeats", type=int, default=3)
    parser.add_argument("--warmup-requests", type=int, default=100)
    parser.add_argument(
        "--suite",
        choices=("baseline", "variants", "all"),
        default="all",
        help="benchmark only the matching Compose profile or all services",
    )
    parser.add_argument(
        "--connection-mode",
        choices=("keepalive", "new"),
        default="keepalive",
        help="reuse HTTP connections or create a new connection per request",
    )
    parser.add_argument("--json-out", help="write detailed results to JSON")
    parser.add_argument("--csv-out", help="write summary results to CSV")
    parser.add_argument(
        "--docker-stats-out",
        help="write a docker stats snapshot to JSON after the benchmark",
    )
    args = parser.parse_args()

    all_targets = [
        ("baseline", "Django", 8101),
        ("baseline", "FastAPI", 8102),
        ("baseline", "Django-Bolt", 8103),
        ("baseline", "Go Echo", 8104),
        ("baseline", "Rust Axum", 8105),
        ("baseline", "PHP native", 8106),
        ("baseline", "Node native", 8107),
        ("baseline", "Java native", 8108),
        ("baseline", "Express", 8109),
        ("baseline", "Fastify", 8110),
        ("baseline", "C# ASP.NET", 8111),
        ("baseline", "C++ native", 8112),
        ("variants", "Django uWSGI 4", 8113),
        ("variants", "Django Waitress 4", 8114),
        ("variants", "Django Gunicorn 4", 8116),
        ("variants", "Django Uvicorn 4", 8117),
        ("variants", "Django Gunicorn 2", 8118),
        ("variants", "Gunicorn gthread 4x4", 8119),
        ("variants", "Django Uvicorn 1 asyncio", 8120),
        ("variants", "Django Uvicorn 4 optimized", 8121),
        ("variants", "Go Echo 4 workers", 8122),
        ("variants", "Rust Axum 4 workers", 8123),
        ("variants", "Java 4 workers", 8124),
        ("variants", "C++ 4 workers", 8125),
    ]
    targets = [
        (name, port)
        for suite, name, port in all_targets
        if args.suite == "all" or args.suite == suite
    ]

    print(
        f"requests={args.requests} repeats={args.repeats} "
        f"warmup={args.warmup_requests} concurrency={args.concurrency} "
        f"connection_mode={args.connection_mode} suite={args.suite}\n"
    )
    print(
        f"{'server':<30} {'req/s':>10} {'avg ms':>10} {'median':>10} "
        f"{'p95 ms':>10} {'p99 ms':>10} {'errors':>8}"
    )
    print("-" * 94)

    results = []
    for target in targets:
        result = run_target(target, args)
        results.append(result)
        print(
            f"{result['server']:<30} {result['rps']:>10.1f} "
            f"{result['avg_ms']:>10.2f} {result['median_ms']:>10.2f} "
            f"{result['p95_ms']:>10.2f} {result['p99_ms']:>10.2f} "
            f"{result['errors']:>8}"
        )

    write_results(results, args)
    if args.docker_stats_out:
        stats = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "containers": collect_docker_stats(),
        }
        path = Path(args.docker_stats_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
