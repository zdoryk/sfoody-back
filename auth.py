from time import time
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pymongo import MongoClient
from env_variables import SECRET_KEY, ALGORITHM, CLIENT


client = CLIENT
# client = MongoClient()
db = client['Sfoodie']
users = db['USERS']


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"user": "Can access to user data.", "admin": "Can do anything."},
)


async def get_authorized(security_scopes: SecurityScopes, request: Request,  token: str = Depends(oauth2_scheme)):
    print(request.url.path.split('/')[-1])
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": authenticate_value},
    )
    # print(f'{authenticate_value=}')

    try:
        # print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(payload)
        email: str = payload.get("sub")
        exp: int = payload.get("exp")
        user_id: int = payload.get("user_id")
        token_scope: str = payload.get("scope")
        # print(f'{token_scope=}')
        if exp < time():
            raise credentials_exception
        if email is None:
            raise credentials_exception
        if len(await request.body()) > 0:
            request_body = await request.json()
            print(request_body)
            # If user tries to modify records of another user and user is not an admin
            if user_id != request_body['user_id'] and token_scope == 'user':
                credentials_exception.detail = 'You provided user_id of another user'
                raise credentials_exception
        else:
            id_from_path = request.url.path.split('/')[-1]
            if id_from_path.isdigit():
                if token_scope == 'user' and user_id != int(id_from_path):
                    credentials_exception.detail = 'You provided user_id of another user'
                    raise credentials_exception
            else:
                query = request.query_params
                if query.items() and token_scope == 'user' and user_id != int(query.get("user_id")):
                    credentials_exception.detail = 'You provided user_id of another user'
                    raise credentials_exception

    except JWTError:
        raise credentials_exception
    print(security_scopes.scopes)
    print(token_scope)
    for scope in security_scopes.scopes:
        # print(f'{scope=}')
        if scope not in token_scope:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
