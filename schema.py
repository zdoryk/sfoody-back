from pydantic import BaseModel
from typing import List


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    user_id: int
    email: str | None = None
    disabled: bool | None = None


class NewUser(BaseModel):
    email: str
    password: str


class UserInDB(User):
    hashed_password: str
    role: str


# Receipts


class Product(BaseModel):
    product_name: str
    price: float


class UserReceipt(BaseModel):
    user_id: int
    receipt_id: int | None = None
    createdAt: int | None = None
    total_price: float | None = None
    products: List[Product] | None = None


# Products

class UserProduct(BaseModel):
    product_name: str


class UserCategory(BaseModel):
    category_name: str
    color: str
    ico: str
    products: List[UserProduct] | None = None


class UserProducts(BaseModel):
    user_id: int
    categories: List[UserCategory]


class NewCategoryRequest(UserCategory):
    user_id: int


class UserReplaceCategory(BaseModel):
    user_id: int
    old_category: str
    new_category: str
    new_product_name: str


class UpdateUserProduct(UserReplaceCategory):
    old_product_name: str
