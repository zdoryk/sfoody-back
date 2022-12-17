from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "6f46b11750f41a8687d98c4f8eef7fa556e813c4a3db1c583cf44b5922053fe8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

MONGO_LOGIN = "HPFLY"
MONGO_PASS = "a0504905922A"

DEFAULT_USER_CATEGORIES = \
    {
        "Fruits": {
                "ico": "apple",
                "color": "#FF7043",
                "products": [
                ]
            },
            "Meat": {
                "ico": "drumstick",
                "color": "#FF5252",
                "products": [
                ]
            },
            "Drinks": {
                "ico": "drinks",
                "color": "#536DFE",
                "products": [
                ]
            },
            "Semi-finished products": {
                "ico": "pizza",
                "color": "#B388FF",
                "products": [
                ]
            },
            "Snacks": {
                "ico": "candy",
                "color": "#FFA726",
                "products": [
                ]
            },
            "Other": {
                "ico": "questionCircle",
                "color": "#656b69",
                "products": [
                ]
            },
            "Fish": {
                "ico": "fish",
                "color": "#F178B6",
                "products": [
                ]
            },}