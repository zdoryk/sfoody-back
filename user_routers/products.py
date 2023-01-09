from fastapi import APIRouter, Depends, Security, Query
import pymongo.errors
import json
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from auth import get_authorized
from schema import UserProducts, NewCategoryRequest, UserReplaceCategory, UpdateUserProduct
from env_variables import CLIENT

client = CLIENT
# client = MongoClient()
db = client['Sfoodie']

receipts = db['Receipts']
products = db['Products']

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_authorized)],
    responses={404: {"description": "Not found"}},
)


# class UserProduct(BaseModel):
#     product_name: str
#
#
# class UserCategory(BaseModel):
#     category_name: str
#     color: str
#     ico: str
#     products: List[UserProduct] | None = None
#
#
# class UserProducts(BaseModel):
#     user_id: int
#     categories: List[UserCategory]

# *** Only for admin
# @router.get("/", dependencies=[Security(get_authorized, scopes=['admin'])], tags=['admin'])
# async def get_products_of_all_users():
#     return list(products.find({}, {'_id': False}))


@router.get("/{user_id}")
async def get_user_products(user_id: int):
    return products.find_one({"user_id": user_id}, {'_id': False})


@router.put("/put_user_products")
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
        products.insert_one(new_dict)
        return {"answer": "Created new record"}


# class UserReplaceCategory(BaseModel):
#     user_id: int
#     old_category: str
#     new_category: str
#     new_product_name: str


# @router.put("/update_user_product_category")
# async def put_user_category(replacement: UserReplaceCategory):
#     try:
#         # pipeline = [
#         #     {"$match": {"user_id": 1}},
#         #     {"$project": {"_id": 0, "Fruits": {"ico": 1, "color": 1}}}
#         # ]
#         # result = next(products.aggregate(pipeline))
#         # result[replacement.old_category_name]['ico'] = replacement.new_category_ico
#         # result[replacement.old_category_name]['color'] = replacement.new_category_color
#         # result[replacement.new_category_name] = result.pop(replacement.old_category_name)
#
#         result = products.update_one(
#             {"user_id": replacement.user_id, replacement.old_category_name: {"$exists": True}},
#             {
#                 "$set": {
#                     replacement.new_category_name + ".color": replacement.new_category_color,
#                     replacement.new_category_name + ".ico": replacement.new_category_ico
#                 }
#             }
#         )
#
#         if replacement.new_category_name != replacement.old_category_name:
#             result = products.update_one(
#                 {"user_id": replacement.user_id},
#                 {
#                     "$rename": {replacement.old_category_name: replacement.new_category_name},
#                 }
#             )
#             return {f"{result.modified_count} records were updated, category_name was also modified"}
#         return {f"{result.modified_count} records were updated"}
#     except Exception as e:
#         return {"Error": f'{e} There is no record with this user_id: {replacement.user_id}'}


@router.put("/update_user_product")
async def put_user_products(replacement: UpdateUserProduct):
    # data = replacement.dict()
    if products.find_one({"user_id": replacement.user_id}) is not None:
        old_doc = products.find_one({"user_id": replacement.user_id}, {"_id": False})
        print(old_doc)
        for i in range(len(old_doc[replacement.old_category]['products'])):
            if old_doc[replacement.old_category]['products'][i].lower() == replacement.old_product_name.lower():
                old_doc[replacement.old_category]['products'][i] = replacement.new_product_name
        print(replacement)
        print(old_doc[replacement.old_category]['products'])
        old_doc[replacement.old_category]['products'].remove(replacement.new_product_name)
        old_doc[replacement.new_category]['products'].append(replacement.new_product_name.capitalize())

        print(products.find_one_and_replace({"user_id": replacement.user_id}, old_doc))
        if replacement.new_product_name != replacement.old_product_name:
            result = receipts.update_many(
                {"user_id": replacement.user_id, "products.product_name": f"{replacement.old_product_name}"},
                {"$set": {"products.$.product_name": f"{replacement.new_product_name}"}}
            )
            print(f"{result.modified_count} receipts were modified")
            return {f"{result.modified_count} receipts were modified"}
        return {"OK"}
    else:
        return {"Error": f'There is no record with this user_id: {replacement.user_id}'}


@router.post("/post_user_products")
async def post_user_products(user_products: UserProducts):
    try:
        products.insert_one(json.loads(user_products.json()))
        return {"answer": "Created new record"}
    except pymongo.errors.WriteError as e:
        return {"answer": "Error", "comment": "There is a record with this user_id"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


# class NewCategoryRequest(UserCategory):
#     user_id: int


@router.post("/post_new_user_category")
async def post_new_user_category(new_category: NewCategoryRequest):
    try:
        old = products.find_one({'user_id': new_category.user_id}, {"_id": False})

        old[new_category.category_name] = {
            'ico': new_category.ico,
            'color': new_category.color,
            'products': []
        }
        products.find_one_and_replace({'user_id': old['user_id']}, old)
        return {"answer": "New category has been created"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


class NewProductRequest(BaseModel):
    user_id: int
    new_product_name: str
    new_category_name: str


@router.post("/post_new_user_product")
async def post_new_user_product(new_product: NewProductRequest):
    try:
        # Verification about if there is a product with the same name and if the category name is written correctly is on
        # Front end side
        print(new_product)
        products.update_one(
            {'user_id': new_product.user_id},
            {'$push': {f'{new_product.new_category_name}.products': new_product.new_product_name.capitalize()}}
        )
        return {"answer": "New Product has been created"}
    except Exception as e:
        return {"answer": "Error", "comment": e}


@router.delete("/{user_id}")
async def delete_all_user_products(user_id: int):
    if products.find_one_and_delete({"user_id": user_id}) is not None:
        return {"Status": "OK", "Comment": "Products have been deleted"}
    else:
        return {"Status": "Error", "Comment": f"There is no user with user_id: {user_id}"}


@router.delete("/delete_user_product/")  # ?user_id=8&category_name=New_test_category&product_name=Very_new_test_product'
async def delete_user_product(user_id: int = Query(..., gt=0), category_name: str = Query(...), product_name: str = Query(...)):
    try:
        result = products.update_one(
            {"user_id": user_id, f"{category_name}.products": product_name},
         {"$pull": {f"{category_name}.products": product_name}}
        )
        return {"detail": "Success"}
    except Exception as e:
        return e


@router.delete("/delete_user_category/")  # ?user_id=8&category_name=New_test_category&product_name=Very_new_test_product'
async def delete_user_category(user_id: int = Query(..., gt=0), category_name: str = Query(...)):
    try:
        result = products.update_one(
            {"user_id": user_id},
            {"$unset": {category_name: ""}}
        )
        return {"detail": result.modified_count}
    except Exception as e:
        return e