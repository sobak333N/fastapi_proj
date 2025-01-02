alembic init migrations
alembic upgrade head
alembic revision --autogenerate -m "Initial migration"

root@root.ru root

mongosh "mongodb://mongo:mongo@localhost:27017/mongo?authSource=admin"



mongo> db.lesson.deleteMany({lesson_name:'lesson_name'})
{ acknowledged: true, deletedCount: 4 }
mongo> db.lesson.deleteMany({})
{ acknowledged: true, deletedCount: 2 }
mongo> db.lesson.find().pretty()

