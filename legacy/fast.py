import hashlib
import pymongo.errors
from bson import ObjectId
from fastapi import FastAPI, Depends, Request, HTTPException, status, Response, Header
from fastapi.responses import HTMLResponse
# import db as db_func
import json
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING, ReturnDocument
import itertools
import time
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from env_variables import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS
from dependencies import get_user, oauth2_scheme, pwd_context, User, get_current_user
from auth import get_authorized

client = MongoClient()
db = client['Sfoody']

receipts = db['Receipts']
# products = db['Products']
products = db['TEST']

# Create object of a class FastAPI
app = FastAPI()

# Pick origins wich can get data
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:*",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


###
##
#
##########  Default
#
##
###

@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>There is nothing here, to see api docs - please follow this link: <a href=http://localhost:8000/docs> 
            docs</a></h1>
        </body>
    </html>
    """


###
##
#
######### Token
#
##
###

class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


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


@app.post("/token", response_model=Token)
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


# @app.middleware("http")
# async def is_authorized(request: Request, call_next):
#     if get_current_active_user():
#         response = await call_next(request)
#         return response
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Please login to make this request",
#         )


###
##
#
##########  Receipts
#
##
###


class Product(BaseModel):
    product_name: str
    price: float


class UserReceipt(BaseModel):
    user_id: int
    receipt_id: int
    createdAt: int
    total_price: float
    products: List[Product]


@app.get("/receipts/")
async def get_receipts_of_all_users():
    try:
        return list(receipts.find({}, {'_id': False}))
    except Exception as e:
        return e


@app.get("/receipts/{user_id}", dependencies=[Depends(get_authorized)])
async def get_users_receipts(user_id: int):
    try:
        return list(receipts.find({"user_id": user_id}, {'_id': False}))
    except Exception as e:
        return e


class UserReceiptPost(BaseModel):
    user_id: int
    createdAt: int
    total_price: float
    products: List[Product]


# def check_and_update_user_products(new_receipt):
#     new_products = new_receipt['products']
#     user_products_document = products.find_one({"user_id": new_receipt['user_id']})
#     print(user_products_document)
#     user_products = user_products_document['products']
#     user_products_lower = [x.lower() for x in user_products]
#
#     new_products = [x.capitalize() for x in new_products if x.lower() not in user_products_lower]
#     new_products_with_categories = []
#
#     for i in new_products:
#         new_products_with_categories.append(
#             {
#                 "product_name": i,
#                 "category": "Other"
#             }
#         )
#
#     user_products.extend(new_products_with_categories)
#     user_products_document['products'] = user_products
#     print(user_products_document)
#
#     return user_products_document


# 1. Check if there is a receipt with same userId and createdAt
# 2. If in this receipt are new products add them to "products" collection
@app.post("/receipts/post_user_receipt")
async def post_user_products(receipt: UserReceiptPost):
    new_receipt = receipt.dict()
    # Check if there is receipt with same user_id and createdAt parameters
    if receipts.find_one({"$and": [{"user_id": receipt.user_id}, {"createdAt": receipt.createdAt}]}) is None:
        # Get last receipt_id for user with this user_id
        new_receipt['receipt_id'] = \
        list(receipts.find({'user_id': receipt.user_id}, sort=[("receipt_id", -1)], limit=1))[0]['receipt_id'] + 1
        # Generate '_id'
        to_hash = (str(new_receipt['user_id']) + '-' + str(new_receipt['receipt_id']) + '-' + str(
            new_receipt['createdAt']))
        new_receipt['_id'] = ObjectId(hashlib.sha1(to_hash.encode("UTF-8")).hexdigest()[:24])
        try:
            print(new_receipt)
            # Get all products from this receipt
            new_products = [x['product_name'].lower() for x in new_receipt['products']]
            print(new_products)
            # Get document with all products of this user from db
            user_products_document = products.find_one({'user_id': new_receipt['user_id']}, {'_id': False})
            # Copy this document
            new_user_products_document = user_products_document.copy()
            # Delete suer_id from old document
            user_products_document.pop('user_id')
            # Get all products from document
            user_products = list(
                itertools.chain.from_iterable([x['products'] for x in user_products_document.values()]))
            user_products_lower = [y.lower() for y in user_products]
            # Check if there are any products that aren't currently in our db
            new_products = [x.capitalize() for x in new_products if x.lower() not in user_products_lower]
            # new_products_with_categories = []

            # for i in new_products:
            #     new_products_with_categories.append(
            #         {
            #             "product_name": i,
            #             "category": "Other"
            #         }
            #     )
            # Add this products to "Other" category
            new_user_products_document['Other']['products'].extend(new_products)
            # Insert new receipt and replace existing record of all products in db
            receipts.insert_one(new_receipt)
            products.find_one_and_replace({"user_id": new_receipt['user_id']}, new_user_products_document)

            return {"Status": "OK", "Comment": f"New receipt has been created. Receipt_id: {new_receipt['receipt_id']}"}
            # return {"Status": "OK", "Comment": f"New receipt has been created. Receipt_id: {new_receipt['receipt_id']}"}
        except Exception as e:
            return {"Status": "Error", "Comment": e}
    else:
        print('qwe')
        return {"Status": "Error", "Comment": "There is receipt with this receipt_id"}


@app.put("/receipts/put_user_receipt")
async def put_user_products(receipt: UserReceipt):
    if receipts.find_one({"$and": [{"user_id": receipt.user_id}, {"receipt_id": receipt.receipt_id},
                                   {"createdAt": receipt.createdAt}]}) is None:
        receipts.insert_one(json.loads(receipt.json()))
        return {"Status": "OK", "Comment": "New receipt has been created"}
    else:
        receipts.find_one_and_replace(filter={"$and": [{"user_id": receipt.user_id}, {"receipt_id": receipt.receipt_id},
                                                       {"createdAt": receipt.createdAt}]},
                                      replacement=json.loads(receipt.json()))
        return {"Status": "OK", "Comment": "Existing receipt has been updated"}


class UserReceiptDelete(BaseModel):
    user_id: int
    receipt_id: int


@app.delete("/receipts/delete_user_receipt")
async def delete_user_receipt(receipt: UserReceiptDelete):
    print(receipt)
    try:
        receipts.find_one_and_delete({"$and": [{"user_id": receipt.user_id}, {"receipt_id": receipt.receipt_id}]})
        return {"Status": "OK", "Comment": f"User's receipt {receipt.receipt_id} has been deleted"}
    except Exception as e:
        return {"Status": "Error", "Comment": e}
    # if receipts.find_one_and_delete({"$and": [{"user_id": receipt.user_id}, {"receipt_id": receipt.receipt_id}]}) is not None:
    #     return {"Status": "OK", "Comment": f"User's receipt {receipt.receipt_id} has been deleted"}
    # else:
    #     return {"Status": "Error", "Comment": f"There is no receipt with: user_id: {receipt.user_id} receipt_id: {receipt.receipt_id}"}


###
##
#
##########  Products
#
##
###


# class UserProduct(BaseModel):
#     product_name: str
#     category: str


class UserProduct(BaseModel):
    product_name: str


# class UserCategory(BaseModel):
#     category_name: str
#     color: str
#     ico: str


class UserCategory(BaseModel):
    category_name: str
    color: str
    ico: str
    products: List[UserProduct]


# class UserProducts(BaseModel):
#     user_id: int
#     products: List[UserProduct]
#     categories: List[UserCategory]


class UserProducts(BaseModel):
    user_id: int
    categories: List[UserCategory]


@app.get("/products")
async def get_products_of_all_users():
    return list(products.find({}, {'_id': False}))


@app.get("/products/{user_id}")
async def get_user_products(user_id: int):
    return products.find_one({"user_id": user_id}, {'_id': False})


# @app.put("/products/put_user_products")
# async def put_user_products(user_products: UserProducts):
#     if products.find_one({"user_id": user_products.user_id}) is not None:
#         products.find_one_and_replace(filter={"user_id": user_products.user_id},
#                                       replacement=json.loads(user_products.json()))
#         return {"answer": "Updated existing record"}
#     else:
#         # new_user_id = products.find_one(sort=[("user_id", DESCENDING)]).get("user_id") + 1
#         # user_products.user_id = new_user_id
#         products.insert_one(json.loads(user_products.json()))
#         return {"answer": "Created new record"}


@app.put("/products/put_user_products")
async def put_user_products(user_products: UserProducts):
    new_dict = {
        "user_id": user_products.dict()['user_id']
    }
    for i in user_products.dict()['categories']:
        new_dict[i['category_name']] = {
            'color': i['color'],
            'ico': i['ico'],
            'products': [x['product_name'] for x in i['products']]
        }
    if products.find_one({"user_id": user_products.user_id}) is not None:
        products.find_one_and_replace(filter={"user_id": user_products.user_id},
                                      replacement=new_dict)
        return {"answer": "Updated existing record"}
    else:
        # new_user_id = products.find_one(sort=[("user_id", DESCENDING)]).get("user_id") + 1
        # user_products.user_id = new_user_id
        products.insert_one(new_dict)
        return {"answer": "Created new record"}
    # return {"answer": "New record"}


class UserReplaceCategory(BaseModel):
    user_id: int
    old_category: str
    new_category: str
    product_name: str


@app.put("/products/replace_user_product_category")
async def put_user_products(replacement: UserReplaceCategory):
    if products.find_one({"user_id": replacement.user_id}) is not None:
        old_doc = products.find_one({"user_id": replacement.user_id}, {"_id": False})
        old_doc[replacement.old_category]['products'].remove(replacement.product_name)
        old_doc[replacement.new_category]['products'].append(replacement.product_name)
        print(old_doc)
        products.find_one_and_replace({"user_id": replacement.user_id}, old_doc)
        return {"status": '200 OK'}
    else:
        return {"Error": f'There is no record with this user_id: {replacement.user_id}'}
    # except Exception as e:
    #     return {e}


class UpdateUserProduct(BaseModel):
    user_id: int
    old_category: str
    new_category: str
    old_product_name: str
    new_product_name: str


@app.put("/products/update_user_product")
async def put_user_products(replacement: UpdateUserProduct):
    data = replacement.dict()
    if products.find_one({"user_id": replacement.user_id}) is not None:
        old_doc = products.find_one({"user_id": replacement.user_id}, {"_id": False})
        # if replacement.old_product_name.lower() != replacement.old_product_name.lower():
        #     old = products.find_one({"user_id": replacement.user_id}, {"_id": False})
        #     new_products = []
        #     for product in old['products']:
        #         if product == replacement.old_product_name:
        #             new_products.append(replacement.new_product_name)
        #         else:
        #             new_products.append(product)
        #     new_document = products.find_one_and_update({'user_id': 1},
        #                              {'$set': {f'{replacement.old_category}.products': old[replacement.old_category]['products']}},
        #                              return_document=ReturnDocument.AFTER)
        #     if replacement.old_category.lower() != replacement.new_category.lower():
        #         new_document[replacement.old_category]['products'].remove(replacement.new_product_name)
        #         new_document[replacement.new_category]['products'].append(replacement.new_product_name)
        #         products.find_one_and_replace({"user_id": replacement.user_id}, new_document)

        for i in range(len(old_doc[replacement.old_category]['products'])):
            if old_doc[replacement.old_category]['products'][i].lower() == replacement.old_product_name.lower():
                old_doc[replacement.old_category]['products'][i] = replacement.new_product_name.capitalize()

        old_doc[replacement.old_category]['products'].remove(replacement.new_product_name)
        old_doc[replacement.new_category]['products'].append(replacement.new_product_name)

        print(products.find_one_and_replace({"user_id": replacement.user_id}, old_doc))

        return {"status": '200 OK'}
    else:
        return {"Error": f'There is no record with this user_id: {replacement.user_id}'}
    # except Exception as e:
    #     return {e}


@app.post("/products/post_user_products")
async def post_user_products(user_products: UserProducts):
    try:
        products.insert_one(json.loads(user_products.json()))
        return {"answer": "Created new record"}
    except pymongo.errors.WriteError as e:
        return {"answer": "Error", "comment": "There is a record with this user_id"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


class NewCategoryRequest(BaseModel):
    user_id: int
    new_category_name: str
    new_icon_name: str
    new_color_name: str


@app.post("/products/post_new_user_category")
async def post_new_user_category(new_category: NewCategoryRequest):
    try:
        old = products.find_one({'user_id': 1}, {"_id": False})

        old[new_category.new_category_name] = {
            'ico': new_category.new_icon_name,
            'color': new_category.new_color_name,
            'products': []
        }
        products.find_one_and_replace({'user_id': old['user_id']}, old)
        return {"answer": "Created new category"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


class NewProductRequest(BaseModel):
    user_id: int
    new_product_name: str
    new_category_name: str


@app.post("/products/post_new_user_product")
async def post_new_user_product(new_product: NewProductRequest):
    try:
        # Verification about if there is a product with the same name and if the category name is written correctly is on
        # Front end side
        products.update_one(
            {'user_id': new_product.user_id},
            {'$push': {f'{new_product.new_category_name}.products': new_product.new_product_name.capitalize()}}
        )
        return {"answer": "New Product was created"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


@app.delete("/products/{user_id}")
async def delete_all_user_products(user_id: int):
    if products.find_one_and_delete({"user_id": user_id}) is not None:
        return {"Status": "OK", "Comment": "Products have been deleted"}
    else:
        return {"Status": "Error", "Comment": f"There is no user with user_id: {user_id}"}


# Delete only one product needed


###
##
#
##########  Custom
#
##
###

@app.get("/custom/{user_id}")
async def get_all_user_data(user_id: int):
    if products.find_one({"user_id": user_id}) is not None:
        user_products = {"categories": products.find_one({"user_id": user_id}, {"_id": False})}
        if receipts.find_one({"user_id": user_id}) is not None:
            user_receipts = list(receipts.find({"user_id": user_id}, {"_id": False}))
            user_products['receipts'] = user_receipts
            user_products['new_user'] = False

            print(f"User products = {user_products}\n")
        else:
            user_products['receipts'] = []
            user_products['new_user'] = True
        return user_products
    else:
        return {"Status": "Error", "Comment": f"There is no user with user_id: {user_id}"}
