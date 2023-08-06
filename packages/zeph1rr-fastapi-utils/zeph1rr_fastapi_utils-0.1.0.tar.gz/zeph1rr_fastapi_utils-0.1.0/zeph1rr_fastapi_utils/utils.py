import json
from uuid import UUID
from datetime import datetime
from datetime import timedelta

from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi import status
from fastapi import Header

def verify_token(header=Header(..., alias="WWW-Authorization")):
    """
    Function to verify authorization header with json web token

    :param header: request header named "WWW-Authorization"
    :type header: fastapi.Header
    """
    try:
        token = header.split("Bearer")[1].strip()
        return token
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невалидный заголовок авторизации",
        )
    
class UUIDEncoder(json.JSONEncoder):
    """Encoder for uuid to json responses"""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class AuthService:
    def __init__(self, expire: timedelta):
        self.pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.expire = expire

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.expire
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.jwt_secret, algorithm="HS256"
        )
        return encoded_jwt
