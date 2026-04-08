migrations:
	alembic revision --autogenerate -m "initial commit"

migrate:
	alembic upgrade head

down-migrate:
	alembic downgrade -1

current-mig:
	alembic current