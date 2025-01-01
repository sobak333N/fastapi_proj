alembic init migrations
alembic upgrade head
alembic revision --autogenerate -m "Initial migration"

root@root.ru root

mongosh "mongodb://mongo:mongo@localhost:27017/mongo?authSource=admin"
