from contextlib import asynccontextmanager
from typing import Any
import uuid

from aiobotocore.session import get_session 
from fastapi import File

from app.config import Config
from app.errors import FileIsTooLarge

class S3Client:
    def __init__(self):
        self.config = {
            "aws_access_key_id": Config.S3_ACCESS_KEY,  
            "aws_secret_access_key": Config.S3_SECRET_ACCESS_KEY,
            "endpoint_url": Config.S3_URL,
            "region_name": Config.REGION,
        }
        self.bucket_name = Config.S3_BUCKET
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self): 
        async with self.session.create_client("s3", **self.config) as client:
            yield client
            
    async def upload_file(self, file: File):
        file_content = await file.read()
        file_key = str(uuid.uuid4())
        
        if len(file_content) > Config.MAX_FILE_SIZE:
            raise FileIsTooLarge()

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
            )

        return f"{self.config['endpoint_url']}/{self.bucket_name}/{file_key}"

    async def delete_file(self, file_key: str):
        """
        Удаляет файл из S3 по его ключу (Key).
        :param file_key: Ключ файла в S3.
        """
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key,
            )