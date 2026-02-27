sync:
	uv sync --all-groups

format:
	uvx ruff format . --no-cache --respect-gitignore --config pyproject.toml
# --quiet for not detail or --verbose for detail

lint:
	uvx ruff check . --fix --no-cache --respect-gitignore --config pyproject.toml --exit-zero

type_check:
	uvx ty check --exit-zero

security_check:
	uvx bandit -r src/ --configfile pyproject.toml --exit-zero

precommit_check:
	uvx pre-commit run --all-files

build:
	uv build --clear --upgrade --quiet

clean:
	uvx ruff clean ; uv clean

stage_changes:
	git add .

all: sync format lint type_check security_check build clean precommit_check stage_changes
