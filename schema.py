from pydantic import BaseModel
from typing import List


class UpdateEmail(BaseModel):
    user_id: int
    new_email: str


class UpdatePassword(BaseModel):
    user_id: int
    old_password: str
    new_password: str


class UpdateCurrency(BaseModel):
    user_id: int
    new_currency: str


class ExportDataFormats(BaseModel):
    xslx: bool | None = None # Temp
    csv: bool
    json_: bool


class ExportDataCategories(BaseModel):
    products: bool
    all_receipts: bool


class ExportData(BaseModel):
    user_id: int
    categories: ExportDataCategories
    formats: ExportDataFormats




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
    currency: str


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
    old_category_name: str
    new_category_name: str
    # old_category_ico: str
    new_category_ico: str
    # old_category_color: str
    new_category_color: str


class UpdateUserProduct(BaseModel):
    user_id: int
    old_category: str
    new_category: str
    new_product_name: str
    old_product_name: str
