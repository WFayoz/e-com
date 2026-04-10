migrations:
	alembic revision --autogenerate -m "initial commit"

migrate:
	alembic upgrade head

down-migrate:
	alembic downgrade -1

current-mig:
	alembic current

test:
	./.venv/bin/python -m unittest tests/test_critical_paths.py
