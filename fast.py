import hashlib

import pymongo.errors
from bson import ObjectId
from fastapi import FastAPI
# import db as db_func
import json
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING


client = MongoClient()
db = client['Sfoody']

receipts = db['Receipts']
products = db['Products']

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


@app.get("/receipts/{user_id}")
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


@app.post("/receipts/post_user_receipt")
async def post_user_products(receipt: UserReceiptPost):
    new_receipt = receipt.dict()
    if receipts.find_one({"$and": [{"user_id": receipt.user_id}, {"createdAt": receipt.createdAt}]}) is None:
        new_receipt['receipt_id'] = list(receipts.find({'user_id': receipt.user_id}, sort=[("receipt_id", -1)], limit=1))[0]['receipt_id'] + 1
        to_hash = (str(new_receipt['user_id']) + '-' + str(new_receipt['receipt_id']) + '-' + str(new_receipt['createdAt']))
        new_receipt['_id'] = ObjectId(hashlib.sha1(to_hash.encode("UTF-8")).hexdigest()[:24])
        try:
            receipts.insert_one(new_receipt)
            return {"Status": "OK", "Comment": "New receipt has been created"}
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


###
##
#
##########  Products
#
##
###


class UserProduct(BaseModel):
    product_name: str
    category: str


class UserCategory(BaseModel):
    category_name: str
    color: str
    ico: str


class UserProducts(BaseModel):
    user_id: int
    products: List[UserProduct]
    categories: List[UserCategory]


@app.get("/products")
async def get_products_of_all_users():
    return list(products.find({}, {'_id': False}))


@app.get("/products/{user_id}")
async def get_user_products(user_id: int):
    return products.find_one({"user_id": user_id}, {'_id': False})


@app.put("/products/put_user_products")
async def put_user_products(user_products: UserProducts):
    if products.find_one({"user_id": user_products.user_id}) is not None:
        products.find_one_and_replace(filter={"user_id": user_products.user_id},
                                      replacement=json.loads(user_products.json()))
        return {"answer": "Updated existing record"}
    else:
        # new_user_id = products.find_one(sort=[("user_id", DESCENDING)]).get("user_id") + 1
        # user_products.user_id = new_user_id
        products.insert_one(json.loads(user_products.json()))
        return {"answer": "Created new record"}


@app.post("/products/post_user_products")
async def post_user_products(user_products: UserProducts):
    try:
        products.insert_one(json.loads(user_products.json()))
        return {"answer": "Created new record"}
    except pymongo.errors.WriteError as e:
        return {"answer": "Error", "comment": "There is a record with this user_id"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


@app.delete("/products/{user_id}")
async def delete_user_products(user_id: int):
    if products.find_one_and_delete({"user_id": user_id}) is not None:
        return {"Status": "OK", "Comment": "Products have been deleted"}
    else:
        return {"Status": "Error", "Comment": f"There is no user with user_id: {user_id}"}


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
        user_products = products.find_one({"user_id": user_id}, {"_id": False})
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
