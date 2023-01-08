from fastapi import APIRouter, Depends
import pymongo.errors
from auth import get_authorized
from schema import UpdateEmail, UpdatePassword, UpdateCurrency, ExportData, DeleteUser
from env_variables import CLIENT, pwd_context
import re
from user_routers.token import update_token
import pandas as pd
from io import BytesIO
from fastapi import Response
import json
from datetime import datetime

client = CLIENT
# client = MongoClient()
db = client['Sfoodie']

users = db['USERS']
products = db['Products']
receipts = db['Receipts']

router = APIRouter(
    prefix="/account",
    tags=["account"],
    dependencies=[Depends(get_authorized)],
    responses={404: {"description": "Not found"}},
)


@router.put("/put_user_email")
async def put_user_email(update_email: UpdateEmail):
    try:
        if not re.match(
                r"^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$",
                update_email.new_email):
            return {"Error: 'Email doesn't match the pattern'"}
        users.find_one_and_update(
            {'user_id': update_email.user_id},
            # {"_id": False}, # Filter
            {'$set': {'email': update_email.new_email}},  # Update
            return_document=True  # Return the updated document
        )

        response = await update_token(update_email.new_email)
        return response
        # return "Success"
    except Exception as e:
        return e


@router.put("/put_user_password")
async def put_user_password(update_password: UpdatePassword):
    try:
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*]{8,}$", update_password.new_password):
            return {"Error": "Password doesn't match the pattern", "code": -2}
        hashed_pass = users.find_one({'user_id': update_password.user_id}, {"_id": False})
        print(hashed_pass.get('hashed_password'))
        if not pwd_context.verify(update_password.old_password, hashed_pass.get('hashed_password')):
            return {"Error": "Bad old password", "code": -1}

        # create new hashed pass and update old
        new_hashed_password = pwd_context.hash(update_password.new_password)
        print(new_hashed_password)
        user_doc = users.find_one_and_update(
            {'user_id': update_password.user_id},
            # {"_id": False},  # Filter
            {'$set': {'hashed_password': new_hashed_password}},
            return_document=True
        )

        response = await update_token(user_doc["email"])
        return response
    except Exception as e:
        return e


@router.put("/put_user_currency")
async def put_user_currency(update_currency: UpdateCurrency):
    try:
        if not re.match(r"^[A-Z]{3}$", update_currency.new_currency):
            return {"Error": "Currency doesn't match the pattern"}
        user_doc = users.find_one_and_update(
            {'user_id': update_currency.user_id},
            # {"_id": False}, # Filter
            {'$set': {'currency': update_currency.new_currency}},  # Update
            return_document=True  # Return the updated document
        )

        response = await update_token(user_doc["email"])
        print(response)
        return response
    except Exception as e:
        return e


@router.put("/deactivate_an_account")
async def deactivate_an_account(user_id: DeleteUser):
    print(user_id)
    users.delete_one({"user_id": user_id.user_id})
    products.delete_one({"user_id": user_id.user_id})
    receipts.delete_many({"user_id": user_id.user_id})
    return user_id


def create_json_response(data: dict, name) -> Response:
    print(data)
    json_data = json.dumps(data).encode('utf-8')

    return Response(
        content=json_data,
        media_type='application/json',
        headers={
            'Content-Disposition': f'filename={name}.json'
        }
    )


def create_csv_response(data, name) -> Response:
    csv_buffer = BytesIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    csv_data = csv_buffer.read()

    return Response(
        content=csv_data,
        media_type='text/csv',
        headers={
            'Content-Disposition': f'{name}.csv'
        }
    )


def create_html_response(data, name) -> Response:
    # html_buffer = BytesIO()
    html_temp = data.to_html(index=False)

    return Response(
        content=bytes(html_temp, "utf-8"),
        media_type='text/html',
        headers={
            'Content-Disposition': f'{name}.html'
        }
    )

@router.post("/export_data")
async def export_data(request: ExportData):
    result = {}
    response_data = []
    # excel_buffer = BytesIO()
    # writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
    if request.categories.products:
        result['products'] = products.find_one({'user_id': request.user_id}, {"_id": False})
        if request.formats.csv:
            df_products = pd.DataFrame(result.get('products'))
            csv_products_response = create_csv_response(df_products, 'products')
            response_data.append(csv_products_response)
        if request.formats.html:
            df_products = pd.DataFrame(result.get('products'))
            html_products_response = create_html_response(df_products, 'products')
            response_data.append(html_products_response)
        # if request.formats.xslx:
        #     df_products = pd.DataFrame(result.get('products'))
        #     # df_products = pd.DataFrame(json.loads(json.dumps(result.get('products')).encode('ISO-8859-1').strip()))
        #     df_products.to_excel(writer, sheet_name='Products')
        if request.formats.json_:
            json_products_response = create_json_response(result.get('products'), 'products')
            response_data.append(json_products_response)
    if request.categories.all_receipts:
        temp_receipts = list(receipts.find({'user_id': request.user_id}, {"_id": False, "receipt_id": False}))
        for receipt in temp_receipts:
            receipt['createdAt'] = datetime.fromtimestamp(receipt.get('createdAt')).strftime("%Y-%m-%d %H:%M:%S")
        result['receipts'] = temp_receipts

        if request.formats.csv:
            df_receipts = pd.DataFrame(result.get('receipts'))
            csv_receipts_response = create_csv_response(df_receipts, 'receipts')
            response_data.append(csv_receipts_response)
        # if request.formats.xslx:
        #     df_receipts = pd.DataFrame(result.get('receipts'))
        #     df_receipts.to_excel(writer, sheet_name='Receipts')
        if request.formats.html:
            df_receipts = pd.DataFrame(result.get('receipts'))
            html_receipts_response = create_html_response(df_receipts, 'receipts')
            response_data.append(html_receipts_response)
        if request.formats.json_:
            json_receipts_response = create_json_response(result.get('receipts'), 'receipts')
            response_data.append(json_receipts_response)

    # writer.save()
    # excel_buffer.seek(0)
    #
    # # print(excel_buffer.read())
    # if request.formats.xslx:
    #     response_data.append(Response(
    #     # print(Response(
    #         content=excel_buffer,
    #         media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    #         headers={
    #             'Content-Disposition': 'data.xlsx'
    #         }
    #     ))

    return tuple(response_data)

