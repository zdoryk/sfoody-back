import time
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pymongo import MongoClient
from env_variables import SECRET_KEY, ALGORITHM

client = MongoClient()
db = client['Sfoody']
users = db['USERS']


fake_users_db = users.find_one({'email': 1}, {'_id': False})


class TokenData(BaseModel):
    email: str | None = None


class User(BaseModel):
    user_id: int
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(email: str):
    user = users.find_one({'email': email}, {'_id': False})
    if user:
        return UserInDB(**user)



