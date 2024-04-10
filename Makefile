
.PHONY: help setup dev_install test_install manifest dev

help:
	@echo "Usage:"

setup:
	@command -v uv >/dev/null 2>&1 || python -m pip install -U uv

dev_install:
	uv pip install -e ".[dev]"
	cd polkastakesphere_dm/dbt && dbt deps && cd ../..

test_install: uv_install
	uv pip install -e ".[tests]"

manifest:
	cd polkastakesphere_dm/dbt && dbt parse && cd ../..

dev:
	make manifest
	dagster dev

lint:
	sqlfluff lint ./polkastakesphere_dm/dbt/models --processes 4

fix:
	sqlfluff fix ./polkastakesphere_dm/dbt/models --processes 4

format:
	ruff --fix . 
