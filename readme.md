alembic init migrations
alembic upgrade head
alembic revision --autogenerate -m "Initial migration"