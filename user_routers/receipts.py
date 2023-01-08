from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from pymongo import MongoClient
from bson import ObjectId
import json

import hashlib
import itertools

from auth import get_authorized
from schema import UserReceipt
from env_variables import CLIENT


client = CLIENT
# client = MongoClient()
db = client['Sfoodie']

receipts = db['Receipts']
products = db['Products']

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    dependencies=[Depends(get_authorized)],
    responses={404: {"description": "Not found"}},
)


# class Product(BaseModel):
#     product_name: str
#     price: float
#
#
# class UserReceipt(BaseModel):
#     user_id: int
#     receipt_id: int | None = None
#     createdAt: int | None = None
#     total_price: float | None = None
#     products: List[Product] | None = None


@router.get("/", tags=['admin'])
async def get_receipts_of_all_users():
    try:
        return list(receipts.find({}, {'_id': False}))
    except Exception as e:
        return e


@router.get("/{user_id}")
async def get_users_receipts(user_id: int):
    try:
        return list(receipts.find({"user_id": user_id}, {'_id': False}))
    except Exception as e:
        return e


# class UserReceiptPost(BaseModel):
#     user_id: int
#     createdAt: int
#     total_price: float
#     products: List[Product]


# 1. Check if there is a receipt with same userId and createdAt
# 2. If in this receipt are new products add them to "products" collection
@router.post("/post_user_receipt")
async def post_user_products(receipt: UserReceipt):
# async def post_user_products(receipt: UserReceiptPost):
    new_receipt = receipt.dict()
    # Check if there is receipt with same user_id and createdAt parameters
    if receipts.find_one({"$and": [{"user_id": receipt.user_id}, {"createdAt": receipt.createdAt}]}) is None:
        # Get last receipt_id for user with this user_id
        if len(list(receipts.find({'user_id': receipt.user_id}))) > 0:
            new_receipt['receipt_id'] = \
            list(receipts.find({'user_id': receipt.user_id}, sort=[("receipt_id", -1)], limit=1))[0]['receipt_id'] + 1
        else:
            new_receipt['receipt_id'] = 1
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
            #     new_products_with_categories.routerend(
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


@router.put("/put_user_receipt")
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


# class UserReceiptDelete(BaseModel):
#     user_id: int
#     receipt_id: int


@router.delete("/delete_user_receipt")
async def delete_user_receipt(receipt: UserReceipt):
# async def delete_user_receipt(receipt: UserReceiptDelete):
    print(receipt)
    try:
        receipts.find_one_and_delete({"$and": [{"user_id": receipt.user_id}, {"receipt_id": receipt.receipt_id}]})
        return {"Status": "OK", "Comment": f"User's receipt {receipt.receipt_id} has been deleted"}
    except Exception as e:
        return {"Status": "Error", "Comment": e}


# # Dev
# @router.delete("/delete_last_receipt")
# async def delete_last():
#     try:
#         receipt_id = receipts.find_one_and_delete({"receipt_id": list(receipts.find({}, sort=[("receipt_id", -1)], limit=1))[0]['receipt_id']})
#         return {"Status": "OK", "Comment": f"User's receipt {receipt_id} has been deleted"}
#     except Exception as e:
#         return {"Status": "Error", "Comment": e}