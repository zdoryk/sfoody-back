import itertools
from functools import reduce

from fastapi import APIRouter, Depends, Security

import pymongo.errors
import json
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from auth import get_authorized
from schema import UserProducts, NewCategoryRequest, UserReplaceCategory, UpdateUserProduct
import pandas as pd
from env_variables import CLIENT

client = CLIENT
# client = MongoClient()
db = client['Sfoodie']

receipts = db['Receipts']
products = db['Products']

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(get_authorized)],
    dependencies=[Security(get_authorized, scopes=['admin'])],
    responses={404: {"description": "Not found"}},
)


@router.get("/get_all_user_data/{user_id}")
# @router.get("/{user_id}", dependencies=[Depends(get_authorized)])
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


@router.get("/get_products_of_all_users")
async def get_products_of_all_users():
    return list(products.find({}, {'_id': False}))


@router.get("/get_receipts_of_all_users")
async def get_receipts_of_all_users():
    try:
        return list(receipts.find({}, {'_id': False}))
    except Exception as e:
        return e

