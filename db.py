import hashlib

import pymongo.errors
from pymongo import MongoClient, DESCENDING
from datetime import datetime
from bson.objectid import ObjectId
import ctypes
import functools
import json


client = MongoClient()
db = client['Sfoody']

receipts = db['Receipts']
products = db['Products']
rec_results = receipts.find()
prod_results = receipts.find()
print(f'{rec_results=}')
print(f'{prod_results=}')

sample_products = [
    # {"product_name": 'Bananas', "price": 3.50},
    # {"product_name": 'Strawberry', "price": 6.43},
    {"product_name": 'Corn Flakes', "price": 2.09},
    # {"product_name": 'Beef', "price": 11.99},
    # {"product_name": 'Pizza', "price": 4.99},
    {"product_name": 'Ham', "price": 3.39},
    # {"product_name": 'Juice', "price": 6.19},
    # {"product_name": 'Snickers', "price": 0.99},
    # {"product_name": 'Lasagne', "price": 7.99},
    {"product_name": 'Ketchup', "price": 0.59},
    # {"product_name": 'Pineapple', "price": 4.99}
  ]


def set_user_products(user_id: int = 1, receipt_id: int = 7, created_at: int = 1644581593):
    to_hash = (str(user_id) + '-' + str(receipt_id) + '-' + str(created_at))
    hashed = hashlib.sha1(to_hash.encode("UTF-8")).hexdigest()[:24]
    data = {
        "_id": ObjectId(hashed),
        "user_id": user_id,
        "receipt_id": receipt_id,
        "createdAt": created_at,
        "products": sample_products
    }
    print(datetime.fromtimestamp(created_at))
    try:
        receipts.insert_one(data)
    except pymongo.errors.DuplicateKeyError as pdk:
        print(f"Duplicate key error: {pdk}")
        return f"Duplicate key error: {pdk}"
    except pymongo.errors.WriteError as pw:
        print(f'Validation error please check data types: {pw}')
        return f'Validation error please check data types: {pw}'
    except Exception as e:
        print(f'Something went wrong: {e}')
        return f'Something went wrong: {e}'


def get_receipt_by_hash(to_hash: str):
    print((hash(to_hash) % 10 ** 12).to_bytes(12, 'big').hex())
    print((hash(to_hash) % 10 ** 12))
    return receipts.find_one({"_id": ObjectId(hashlib.sha1(to_hash.encode("UTF-8")).hexdigest()[:24])})


def get_all_user_receipts(user_id: int = 1):
    return receipts.find_one({"user_id": user_id}, {'_id': False})


def set_total_prices(user_id: int = 1):
    if receipts.find({"user_id": user_id}) is not None:
        # receipts.find_one_and_replace(filter={"user_id": user_id},
        #                               replacement=json.loads(user_products.json()))
        data = list(receipts.find({"user_id": user_id}))
        for receipt in data:
            total_price = functools.reduce(lambda a, b: a + b, [x['price'] for x in receipt['products']])
            receipt['total_price'] = total_price
            receipts.find_one_and_replace(filter={"user_id": user_id, "receipt_id": receipt['receipt_id']},
                                            replacement=receipt)


        return data

# def get_all_products():
#     return list(products.find({}, {'_id': False}))

# print(len(list(products.find({}, {'_id': False}))))
# print(products.count_documents({}))

# date = datetime(2022, 10, 11, 19, 37, 35)
#
# set_user_products(user_id=1, receipt_id=19, created_at=int(date.timestamp()))
# to_hash = (str(1) + '-' + str(7) + '-' + str(1644231861))
# print(get_user_products(to_hash))
# print(get_all_user_receipts())


# print(set_total_prices(1))


# print(receipts.find_one({"$and": [{"user_id": 1}, {"createdAt": 1644398734}]}))

print(list(receipts.find({'user_id': 1}, sort=[("receipt_id", -1)], limit=1))[0]['receipt_id'] + 1)
