import itertools
from functools import reduce

from fastapi import APIRouter, Depends
import pymongo.errors
import json
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from auth import get_authorized
from schema import UserProducts, NewCategoryRequest, UserReplaceCategory, UpdateUserProduct
import pandas as pd

client = MongoClient()
db = client['Sfoody']

receipts = db['Receipts']
products = db['Products']

router = APIRouter(
    prefix="/custom",
    tags=["custom"],
    dependencies=[Depends(get_authorized)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}")
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


@router.get("/tree_map_chart/{user_id}")
async def tree_map_data(user_id: int):
    receipts_all = list(receipts.find({"user_id": user_id}, {"_id": False}))
    # print(pd.DataFrame(receipts_all))
    product_price = list(itertools.chain.from_iterable([x['products'] for x in receipts_all]))
    df = pd.DataFrame(product_price)
    product_price = df.groupby('product_name').sum()['price'].to_dict()

    user_products = products.find_one({"user_id": user_id}, {"_id": False, "user_id": False})
    data = []
    colors = []
    category_summary = []
    for category, value in user_products.items():
        temp_data = []
        price_list = []
        for product, price in product_price.items():
            if product in value['products']:
                temp_data.append({'x': product, 'y': price})
                price_list.append(price)
        if temp_data:
            category_summary.append({'x': category, 'y': sum(price_list)})
            data.append({'name': category, 'data': temp_data})
            colors.append(value['color'])

    return {'tree_map_data': data, 'colors': colors, 'categories_aggregated': {'data': category_summary}    }
    # return category_summary