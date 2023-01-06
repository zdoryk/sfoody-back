from fastapi import APIRouter, Depends
import pymongo.errors
from auth import get_authorized
from schema import UpdateEmail, UpdatePassword, UpdateCurrency
from env_variables import MONGO_LOGIN, MONGO_PASS, pwd_context
import re

client = pymongo.MongoClient(
    f"mongodb+srv://{MONGO_LOGIN}:{MONGO_PASS}@sfoodie.mexl1zk.mongodb.net/?retryWrites=true&w=majority")
# client = MongoClient()
db = client['Sfoodie']

users = db['USERS']

router = APIRouter(
    prefix="/products",
    tags=["account"],
    dependencies=[Depends(get_authorized)],
    responses={404: {"description": "Not found"}},
)


@router.put("/put_user_email")
async def put_user_email(update_email: UpdateEmail):
    try:
        if not re.match(r"/^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i",
                    update_email.new_email):
            return {"Error: 'Email doesn't match the pattern'"}
        users.find_one_and_update(
            {'user_id': update_email.user_id},
            # {"_id": False}, # Filter
            {'$set': {'email': update_email.new_email}},  # Update
            return_document=True  # Return the updated document
        )
        return "Success"
    except Exception as e:
        return e


@router.put("/put_user_password")
async def put_user_password(update_password: UpdatePassword):
    try:
        if not re.match(r"/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*]{8,}$/", update_password.new_password):
            return {"Error": "Password doesn't match the pattern"}
        hashed_pass = users.find_one({'user_id': update_password.user_id}, {"_id": False})
        print(hashed_pass.get('hashed_password'))
        if not pwd_context.verify(update_password.old_password, hashed_pass.get('hashed_password')):
            return {"Error": "Bad old password", "code": -1}

        # create new hashed pass and update old
        new_hashed_password = pwd_context.hash(update_password.new_password)
        print(new_hashed_password)
        users.find_one_and_update(
            {'user_id': update_password.user_id},
            # {"_id": False},  # Filter
            {'$set': {'hashed_password': new_hashed_password}}
        )
        return {"Success"}
    except Exception as e:
        return e


@router.put("/put_user_currency")
async def put_user_currency(update_currency: UpdateCurrency):
    try:
        if not re.match(r"^[A-Z]{3}$", update_currency.new_currency):
            return {"Error": "Currency doesn't match the pattern"}
        users.find_one_and_update(
            {'user_id': update_currency.user_id},
            # {"_id": False}, # Filter
            {'$set': {'currency': update_currency.new_currency}},  # Update
            return_document=True  # Return the updated document
        )
        return "Success"
    except Exception as e:
        return e
