import json
from jose import jwt
import pytest
import requests

from env_variables import SECRET_KEY, ALGORITHM, DEFAULT_USER_CATEGORIES, ADMIN_PASS
from delete_receipts import delete_receipts
from delete_completely import delete_completely

email = ''
password = ''
auth_response = ''
payload = ''
currency: int = 0
user_id: int = 0
token_scope: str = ''
default_user_products = ''
a_email = ''
a_auth_response = ''
a_user_id = 0


@pytest.fixture
def api_url():
    return "http://10.9.179.156:8080"


def test_set_global_values_of_jwt_token(api_url):
    global a_email, a_user_id, a_auth_response, email, password, auth_response, payload, currency, user_id, token_scope, default_user_products
    email = 'new_user_test@gmail.com'
    password = 'NewTest111'
    auth_response = requests.post(f"http://10.9.179.156:8080/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})
    print(auth_response)
    payload = jwt.decode(auth_response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    email = payload.get("sub")
    currency = payload.get("currency")
    user_id = payload.get("user_id")
    token_scope = payload.get("scope")

    # admin

    a_email = "nice.zdorik@gmail.com"
    a_password = ADMIN_PASS
    a_auth_response = requests.post(f"http://10.9.179.156:8080/token",
                                    "username=" + a_email + "&password=" + a_password,
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})

    a_payload = jwt.decode(a_auth_response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    a_user_id = payload.get("user_id")


def test_get_user_receipts_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/receipts/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_user_receipts_with_another_user_id_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/receipts/{1}", headers=headers)
    assert response.status_code == 401


def test_get_user_receipts_with_admin(api_url):
    #
    # headers = {
    #     "Authorization": f"Bearer {a_auth_response.json()['access_token']}",
    #     'accept': 'application/json',
    #     'Content-Type': 'application/json'
    # }
    print(a_auth_response)
    headers = {"Authorization": f"Bearer {a_auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/receipts/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


# POST

def test_post_user_receipts_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = json.dumps({
        "user_id": user_id,
        # "receipt_id": 1,
        "createdAt": 1672527600,  # 01/01/2023
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Apples",
                "price": 3.99
            },
            {
                "product_name": "Beef",
                "price": 7
            }
        ]
    })
    response = requests.post(f"{api_url}/receipts/post_user_receipt", data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": f"New receipt has been created. Receipt_id: {1}"}

    default_user_products_with_new_products = DEFAULT_USER_CATEGORIES
    default_user_products_with_new_products['Other']['products'] = ['Apples', 'Beef']
    default_user_products_with_new_products['user_id'] = user_id

    response = requests.get(f"{api_url}/products/{user_id}", headers=headers)
    print(response)
    assert response.status_code == 200
    print(response)
    assert response.json() == default_user_products_with_new_products

    response = requests.get(f"{api_url}/receipts/{user_id}", headers=headers)
    print(response)
    assert response.status_code == 200
    print(response)
    assert response.json()[0] == {
        "user_id": 8,
        "receipt_id": 1,
        "createdAt": 1672527600,
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Apples",
                "price": 3.99
            },
            {
                "product_name": "Beef",
                "price": 7
            }
        ]
    }


def test_post_user_receipts_admin(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = json.dumps({
        "user_id": user_id,
        "receipt_id": 1,
        "createdAt": 1672527800,
        "total_price": 20.59,
        "products": [
            {
                "product_name": "Pizza",
                "price": 10.59
            },
            {
                "product_name": "Chicken filet",
                "price": 10
            }
        ]
    })
    response = requests.post(f"{api_url}/receipts/post_user_receipt", data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": f"New receipt has been created. Receipt_id: {2}"}

    default_user_products_with_new_products = DEFAULT_USER_CATEGORIES
    default_user_products_with_new_products['Other']['products'] = ['Apples', 'Beef', 'Pizza', 'Chicken filet']
    default_user_products_with_new_products['user_id'] = user_id

    response = requests.get(f"{api_url}/products/{user_id}", headers=headers)
    print(response)
    assert response.status_code == 200
    print(response)
    assert response.json() == default_user_products_with_new_products


def test_post_user_receipts_with_same_createdAt_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = json.dumps({
        "user_id": user_id,
        # "receipt_id": 1,
        "createdAt": 1672527600,  # 01/01/2023
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Apples",
                "price": 3.99
            },
            {
                "product_name": "Beef",
                "price": 7
            }
        ]
    })
    response = requests.post(f"{api_url}/receipts/post_user_receipt", data, headers=headers)
    assert response.status_code == 409
    assert response.json().get('detail') == "There is a receipt with this time"


def test_post_user_receipts_with_another_user_id_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = json.dumps({
        "user_id": 1,
        "receipt_id": 1,
        "createdAt": 1672527600,  # 01/01/2023
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Apples",
                "price": 3.99
            },
            {
                "product_name": "Beef",
                "price": 7
            }
        ]
    })
    response = requests.post(f"{api_url}/receipts/post_user_receipt", data, headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'You provided user_id of another user'


def test_put_user_receipts_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = {
        "user_id": user_id,
        "receipt_id": 1,
        "createdAt": 1672527600,  # 01/01/2023
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Pineapples",
                "price": 3.99
            },
            {
                "product_name": "Tuna",
                "price": 7.0
            }
        ]
    }
    response = requests.put(f"{api_url}/receipts/put_user_receipt", json.dumps(data), headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": "Existing receipt has been updated"}
    response = requests.get(f"{api_url}/receipts/get_user_receipt/?user_id={user_id}&receipt_id={1}", headers=headers)
    assert response.status_code == 200
    assert response.json()[0] == data

    data['receipt_id'] = 777
    data['createdAt'] = 1232527600
    response = requests.put(f"{api_url}/receipts/put_user_receipt", json.dumps(data), headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": "New receipt has been created"}
    response = requests.get(f"{api_url}/receipts/get_user_receipt/?user_id={user_id}&receipt_id={777}", headers=headers)
    assert response.status_code == 200
    assert response.json()[0] == data


def test_put_user_receipts_with_another_user_id_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    data = json.dumps({
        "user_id": 2,
        "receipt_id": 1,
        "createdAt": 1672527600,  # 01/01/2023
        "total_price": 10.99,
        "products": [
            {
                "product_name": "Apples",
                "price": 3.99
            },
            {
                "product_name": "Beef",
                "price": 7
            }
        ]
    })
    response = requests.put(f"{api_url}/receipts/put_user_receipt", data, headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'You provided user_id of another user'


def test_delete_user_receipts_with_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.delete(f"{api_url}/receipts/delete_user_receipt/?user_id={user_id}&receipt_id={1}",
                               headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": f"User's receipt {1} has been deleted"}


def test_delete_user_receipts_with_another_user_id_user(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.delete(f"{api_url}/receipts/delete_user_receipt/?user_id={1}&receipt_id={1}",
                               headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'You provided user_id of another user'


def test_delete_user_receipts_with_admin(api_url):
    headers = {"Authorization": f"Bearer {a_auth_response.json()['access_token']}"}
    response = requests.delete(f"{api_url}/receipts/delete_user_receipt/?user_id={user_id}&receipt_id={2}",
                               headers=headers)
    assert response.status_code == 200
    assert response.json() == {"Status": "OK", "Comment": f"User's receipt {2} has been deleted"}
    response = requests.get(f"{api_url}/receipts/{user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json() == [
        {
            "user_id": 8,
            "receipt_id": 777,
            "createdAt": 1232527600,
            "total_price": 10.99,
            "products": [
                {
                    "product_name": "Pineapples",
                    "price": 3.99
                },
                {
                    "product_name": "Tuna",
                    "price": 7
                }
            ]
        }
    ]
    delete_completely(user_id)

# get by id X
# post_user_receipt X
# put_user_receipt X
# delete_user_receipt X
