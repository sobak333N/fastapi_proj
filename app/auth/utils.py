import re
import logging
import uuid
import string
import random
import jwt
from typing import Tuple
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext

from app.config import Config

passwd_context = CryptContext(schemes=["bcrypt"])




def validate_email(email: str) -> bool:
    if not re.match(r"^.*@.*\..{2,}$", email):
        raise ValueError("Not valid email")
    return True


def validate_password(password: str) -> bool:
    if len(password) < 8:
        raise ValueError("Pass must contain at least 8 symbols")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Pass must contain at least 1 uppercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Pass must contain at least 1 digit")
    if not re.search(r"[\W_]", password):
        raise ValueError("Pass must contain at least 1 special symbol")
    return True

def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)


def create_token(user_data: dict, refresh: bool = False) -> Tuple[str, datetime]:
    payload = {}

    user_data_dict = jsonable_encoder(user_data)
    payload["user"] = user_data_dict
    payload["exp"] = datetime.now() + ( 
        timedelta(days=Config.JWT_REFRESH_EXP_DAYS)
        if refresh 
        else timedelta(minutes=Config.JWT_ACCESS_EXP_MINUTES)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return (token, payload["exp"])


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        return None


def generate_random_token():
    chars = string.ascii_letters + string.digits
    token = "".join([random.choice(chars) for _ in range(16)])
    return token


# def save_token_in_redis(token:str):
#     try:
#         token_data = serializer.loads(token)

#         return token_data
    
#     except Exception as e:
#         logging.error(str(e))
        