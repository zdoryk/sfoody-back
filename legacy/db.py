import hashlib

import pymongo.errors
from pymongo import MongoClient, DESCENDING, ReturnDocument
from datetime import datetime
from bson.objectid import ObjectId
import ctypes
import functools
import json
import itertools



client = MongoClient()
db = client["Sfoody"]

receipts = db["Receipts"]
products = db["Products"]
test = db["TEST"]
# rec_results = receipts.find()
# prod_results = receipts.find()
# print(f"{rec_results=}")
# print(f"{prod_results=}")

sample_products = [
    # {"product_name": "Bananas", "price": 3.50},
    # {"product_name": "Strawberry", "price": 6.43},
    {"product_name": "Corn Flakes", "price": 2.09},
    # {"product_name": "Beef", "price": 11.99},
    # {"product_name": "Pizza", "price": 4.99},
    {"product_name": "Ham", "price": 3.39},
    # {"product_name": "Juice", "price": 6.19},
    # {"product_name": "Snickers", "price": 0.99},
    # {"product_name": "Lasagne", "price": 7.99},
    {"product_name": "Ketchup", "price": 0.59},
    # {"product_name": "Pineapple", "price": 4.99}
  ]


def set_user_products(user_id: int = 1, receipt_id: int = 7, created_at: int = 1644581593):
    to_hash = (str(user_id) + "-" + str(receipt_id) + "-" + str(created_at))
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
        print(f"Validation error please check data types: {pw}")
        return f"Validation error please check data types: {pw}"
    except Exception as e:
        print(f"Something went wrong: {e}")
        return f"Something went wrong: {e}"


def get_receipt_by_hash(to_hash: str):
    print((hash(to_hash) % 10 ** 12).to_bytes(12, "big").hex())
    print((hash(to_hash) % 10 ** 12))
    return receipts.find_one({"_id": ObjectId(hashlib.sha1(to_hash.encode("UTF-8")).hexdigest()[:24])})


def get_all_user_receipts(user_id: int = 1):
    return receipts.find_one({"user_id": user_id}, {"_id": False})


def set_total_prices(user_id: int = 1):
    if receipts.find({"user_id": user_id}) is not None:
        # receipts.find_one_and_replace(filter={"user_id": user_id},
        #                               replacement=json.loads(user_products.json()))
        data = list(receipts.find({"user_id": user_id}))
        for receipt in data:
            total_price = functools.reduce(lambda a, b: a + b, [x["price"] for x in receipt["products"]])
            receipt["total_price"] = total_price
            receipts.find_one_and_replace(filter={"user_id": user_id, "receipt_id": receipt["receipt_id"]},
                                            replacement=receipt)


        return data

# def get_all_products():
#     return list(products.find({}, {"_id": False}))

# print(len(list(products.find({}, {"_id": False}))))
# print(products.count_documents({}))

# date = datetime(2022, 10, 11, 19, 37, 35)
#
# set_user_products(user_id=1, receipt_id=19, created_at=int(date.timestamp()))
# to_hash = (str(1) + "-" + str(7) + "-" + str(1644231861))
# print(get_user_products(to_hash))
# print(get_all_user_receipts())


# print(set_total_prices(1))


# print(receipts.find_one({"$and": [{"user_id": 1}, {"createdAt": 1644398734}]}))

# print(list(receipts.find({"user_id": 1}, sort=[("receipt_id", -1)], limit=1))[0]["receipt_id"] + 1)

default_products = ["Bread", "Chicken", "Salmon",
      "Pasta", "Rice", "Oil", "Ketchup",
      "Salad", "Cereals", "Tomato", "Carrot",
      "Cheese", "Eggs", "Juice", "Milk", "Pineapple"]


# test_products = [x["product_name"] for x in list(receipts.find({"user_id": 1}, sort=[("receipt_id", -1)], limit=1))[0]["products"]]

# default_products = [x.lower() for x in default_products]
# check = [x.capitalize() for x in test_products if x.lower() not in default_products]
#
# result = []
#
# for i in check:
#     result.append(
#         {
#             "product_name": i,
#             "category": "Other"
#         }
#     )
#
# print(check)
# print(result)
#
# p_doc = products.find_one({"user_id": 1})
# p_doc_products = p_doc["products"]
# p_doc_products.extend(result)
# p_doc["products"] = p_doc_products
# print(p_doc)
# .extend(result)
# print(list(receipts.find({"user_id": 1}, sort=[("receipt_id", -1)], limit=1))[0]["products"])

##
###         New product category update
##

# product_name = "apple"
# old_category = "Fruits"
# new_category = "Meat"
# name = "Fruits"
#
# smt = {"qwe": "asd"}
# zxc = "qwe"
#
# old_doc = test.find_one({"user_id": 101}, {"_id": False})
# # new_doc = old_doc
# old_doc[name]["products"].remove(product_name)
# print(old_doc)
# print(old_doc[name]["products"])
# print(old_doc["Fruits"]["products"].remove(product_name))
# print(old_doc["Meat"]["products"].append(product_name))
# print(old_doc)

# test.find_one_and_replace({"user_id": 1}, old_doc)



####

    # Json of all product_names

# list_of_list = [[z["product_name"].lower() for z in x["products"]] for x in list(receipts.find({"user_id": 1}, {"_id": False}))]
# print([x.capitalize() for x in set([item for sublist in list_of_list for item in sublist])])

# ["Strawberry", "Bananas", "Ketchup", "Corn flakes", "Juice", "Beef", "Lasagne", "Pineapple", "Pizza", "Snickers", "Apple", "Ham"]
####


# a = test.find_one({'user_id': 1}, {'_id': False})
# a.pop('user_id')
#
# for value in a.values():
#     print(value['products'])

# print([y.lower() for y in list(itertools.chain.from_iterable([x['products'] for x in a.values()]))])

# Get all products from this receipt
# new_products = ['Salo', 'Maslo', 'Jopa', 'Beef']
# # Get all products for this user from db
# user_products_document = test.find_one({'user_id': 1}, {'_id': False})
# user_products_document.pop('user_id')
# user_products = list(itertools.chain.from_iterable([x['products'] for x in user_products_document.values()]))
# user_products_lower = [y.lower() for y in user_products]
#
# print(user_products)
# print(user_products_lower)
# new_products = [x.capitalize() for x in new_products if x.lower() not in user_products_lower]
#
# user_products_document['Other']['products'].extend(new_products)
# print(user_products_document['Other'])



# user_products_document['products'] = user_products
#
# print(user_products_document)

# receipts.insert_one(new_receipt)
# products.find_one_and_replace({"user_id": new_receipt['user_id']}, user_products_document)

new_category_name = 'Other.products'
icon = 'lol_icon'
color = 'red'

old = test.find_one({'user_id': 1}, {"_id": False})
# print(old[new_category_name])
# print(old)

old['lol'] = {
    'ico': icon,
    'color': color,
    'products': []
}
print(old)
test.update_one(
   { 'user_id': 1},
   { '$push': { new_category_name: 'lol' } }
)
# print(test.find_one_and_replace({'user_id': old['user_id']}, old))

# print(test.find_one_and_update({'user_id': 1}, {'$set': {f'{old_category}.products': old[old_category]['products']}},
#                                 return_document=ReturnDocument.AFTER))