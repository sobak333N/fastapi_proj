from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import Config
from app.models import LessonDocument, LessonTaskDocument

async def init_mongo_db():
    client = AsyncIOMotorClient(Config.MONGO_DB_URL)
    await init_beanie(
        database=client[Config.MONGO_DB], 
        document_models=[LessonDocument, LessonTaskDocument]
    )
