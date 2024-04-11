.PHONY: help prepare_environment install_dev_dependencies install_test_dependencies generate_manifest install_py_tools run_development lint_sql_models fix_sql_models format_code view_leaderboard view_validator_status

help:
	@echo "Usage:"
	@echo "  make install_python_tools         - Installs necessary Python package management tools"
	@echo "  make prepare_environment          - Ensures necessary environment variables are configured"
	@echo "  make install_dev_dependencies     - Installs development dependencies"
	@echo "  make install_test_dependencies    - Installs test-specific dependencies"
	@echo "  make generate_manifest            - Generates the DBT manifest"
	@echo "  make run_dagster_dev              - Executes dagster development tasks including manifest generation"
	@echo "  make view_leaderboard             - Launches Streamlit app for validator leaderboard"
	@echo "  make view_validator_status        - Launches Streamlit app for validator status"
	@echo "  make lint_sql_models              - Lints SQL models for syntax errors"
	@echo "  make fix_sql_models               - Auto-fixes correctable lint errors in SQL models"
	@echo "  make format_code                  - Formats codebase using Ruff"

check_env:
	@if [ -z "$(PSS_PROJECT_ROOT_DIR)" ]; then \
		echo "DEV environment is not active."; \
		echo "Run 'source .activate_env && activate_env' to activate the virtual environment and source environment variables in your shell."; \
		exit 1; \
	fi

install_py_tools:
	@command -v uv >/dev/null 2>&1 || pip install -U uv

prepare_environment: install_py_tools
	@if [ ! -d .venv ]; then \
		echo "Creating virtual environment..."; \
		python -m venv .venv; \
		echo "Virtual environment created."; \
	fi
	@echo "Defining shell function to activate virtual environment and source environment variables..."
	@echo 'activate_env() { . .venv/bin/activate && . ./env.example; }' >> .activate_env
	@echo "Run 'source .activate_env && activate_env' to activate the virtual environment and source environment variables in your shell."

install_dev_dependencies: check_env
	@echo "Installing development dependencies..."
	@. .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "Navigating to DBT directory..."
	@cd polkastakesphere_dm/dbt && dbt deps && cd ../..
	@echo "Development dependencies installed."

install_test_dependencies: check_env
	@uv pip install -e ".[tests]"

generate_manifest: check_env
	@cd polkastakesphere_dm/dbt && dbt parse && cd ../..

run_dagster_dev: check_env
	@make generate_manifest
	@dagster dev

view_leaderboard: check_env
	@streamlit run ./analyze/streamlit/stakings0_leaders_board.py

view_validator_status: check_env
	@streamlit run ./analyze/streamlit/stakings0_validator_status.py

lint_sql_models: check_env
	@sqlfluff lint ./polkastakesphere_dm/dbt/models --processes 4

fix_sql_models: check_env
	@sqlfluff fix ./polkastakesphere_dm/dbt/models --processes 4

format_code: check_env	
	@ruff --fix .

