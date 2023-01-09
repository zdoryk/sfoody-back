from fastapi import Depends, APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient

from env_variables import pwd_context, ACCESS_TOKEN_EXPIRE_DAYS, ALGORITHM, SECRET_KEY, CLIENT, DEFAULT_USER_CATEGORIES
from auth import get_authorized
from schema import Token, User, UserInDB, NewUser

client = CLIENT
# client = MongoClient()
db = client['Sfoodie']

users = db['USERS']
products = db['Products']

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)


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


def generate_token(email: str, user_id: int, scope: str, currency: str):
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": email, 'user_id': user_id, 'currency': currency, "scope": scope},
        expires_delta=access_token_expires
    )
    return access_token


@router.post("/", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    # username here is our email, it's just called username cause of OAuth2 requirements for 'password flow'
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # response = JSONResponse(content={"access_token": generate_token(email=user.email, user_id=user.user_id), "token_type": "bearer"})
    response = JSONResponse(content={"access_token": generate_token(email=user.email, user_id=user.user_id
                                                                    , scope=user.role, currency=user.currency),
                                     "token_type": "bearer"})
    response.set_cookie(
        key="authentication-cookie",
        value=generate_token(email=user.email, user_id=user.user_id, scope=user.role, currency=user.currency),
        httponly=True,
        secure=False,
    )
    return response


# @router.post("/", response_model=Token)
async def update_token(email):
    user = get_user(email)
    response = JSONResponse(content={"access_token": generate_token(email=user.email, user_id=user.user_id
                                                                    , scope=user.role, currency=user.currency),
                                     "token_type": "bearer"})
    response.set_cookie(
        key="authentication-cookie",
        value=generate_token(email=user.email, user_id=user.user_id, scope=user.role, currency=user.currency),
        httponly=True,
        secure=False,
    )
    return response


@router.post("/register", response_model=Token)
# async def register_new_user(new_user: NewUser):
async def register_new_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # list(users.find(sort=[("receipt_id", -1)], limit=1))[0]['user_id'] + 1
    users_db = list(users.find({}, {"_id": False}))
    # Username here is an email
    email = form_data.username
    if email not in [x['email'] for x in users_db]:
        user_id = max(users_db, key=lambda x: x['user_id'])['user_id'] + 1
        users.insert_one({
            "user_id": user_id,
            "email": email,
            "disabled": False,
            "currency": "USD",
            "role": "user",
            "hashed_password": pwd_context.hash(form_data.password)
        })
        new_products = {"user_id": user_id}
        new_products.update(DEFAULT_USER_CATEGORIES)
        products.insert_one(new_products)

        response = JSONResponse(
            content={"access_token": generate_token(email=email, user_id=user_id, scope='user', currency="USD"),
                     "token_type": "bearer"})
        response.set_cookie(
            key="authentication-cookie",
            value=generate_token(email=email, user_id=user_id, scope='user', currency="USD"),
            httponly=True,
            secure=False,
        )
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is a user with same email",
        )

# @router.delete("/delete/{user_id}")
# async def delete_user(response: Response, user_id: int):
#     if users.find_one_and_delete({"user_id": user_id}) is not None:
#         response.status_code = 200
#         response.body = {"Comment": f"User with user_id: {user_id} has been deleted"}
#         return response
#     else:
#         return {"Status": "Error", "Comment": f"There is no user with user_id: {user_id}"}
