from fastapi import Depends, APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient

from env_variables import pwd_context, ACCESS_TOKEN_EXPIRE_DAYS, ALGORITHM, SECRET_KEY
from auth import get_authorized
from schema import Token, User, UserInDB


client = MongoClient()
db = client['Sfoody']

users = db['USERS']

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)


# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# class User(BaseModel):
#     user_id: int
#     email: str | None = None
#     disabled: bool | None = None
#
#
# class UserInDB(User):
#     hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str):
    user = users.find_one({'email': email}, {'_id': False})
    if user:
        return UserInDB(**user)


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    # username here is our email, it's just called username cause of OAuth2 requirements for 'password flow'
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="authentication-cookie",
        value=access_token,
        httponly=True,
        secure=False,
    )
    return response
