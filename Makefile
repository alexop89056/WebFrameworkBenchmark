.DEFAULT_GOAL := help

.PHONY: help baseline variants all smoke-baseline smoke-variants smoke-all \
        benchmark-baseline benchmark-variants benchmark-all clean

help:
	@echo "make baseline             Start baseline services"
	@echo "make variants             Start worker/server variants"
	@echo "make all                  Start both profiles"
	@echo "make smoke-baseline       Check baseline HTTP responses"
	@echo "make smoke-variants       Check variant HTTP responses"
	@echo "make benchmark-all        Run the Python benchmark for all services"
	@echo "make clean                Stop and remove benchmark containers"

baseline:
	docker compose --profile baseline up --build -d --wait

variants:
	docker compose --profile variants up --build -d --wait

all:
	docker compose --profile baseline --profile variants up --build -d --wait

smoke-baseline: baseline
	./scripts/smoke-test.sh baseline

smoke-variants: variants
	./scripts/smoke-test.sh variants

smoke-all: all
	./scripts/smoke-test.sh all

benchmark-baseline: baseline
	python3 benchmark.py --suite baseline

benchmark-variants: variants
	python3 benchmark.py --suite variants

benchmark-all: all
	python3 benchmark.py --suite all

clean:
	docker compose --profile baseline --profile variants down --remove-orphans
