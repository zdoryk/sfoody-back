import json

from jose import jwt
import pytest
import requests

from env_variables import SECRET_KEY, ALGORITHM, DEFAULT_USER_CATEGORIES, ADMIN_PASS
from delete_receipts import delete_receipts

email = ''
password = ''
auth_response = ''
payload = ''
currency: int = 0
user_id: int = 0
token_scope: str = ''
default_user_products = ''

@pytest.fixture
def api_url():
    return "http://10.9.179.156:8080"


def test_set_global_values_of_jwt_token(api_url):
    global email, password, auth_response, payload, currency, user_id, token_scope, default_user_products
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
    default_user_products = DEFAULT_USER_CATEGORIES
    default_user_products['user_id'] = user_id


# /products/{user_id}
def test_get_user_products(api_url):
    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/products/{user_id}", headers=headers)
    assert response.status_code == 200

    assert response.json() == default_user_products


def test_post_new_user_category(api_url):
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "category_name": "New_test_category",
        "color": "test_color",
        "ico": "test_ico",
        "products": [
        ],
        "user_id": user_id
    })
    response = requests.post(f"{api_url}/products/post_new_user_category", data=data, headers=headers)
    assert response.status_code == 200
    assert response.json()['answer'] == 'New category has been created'


def test_post_new_user_product(api_url):
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "user_id": user_id,
        "new_product_name": "new_test_product",  # need to be .lower cause API must capitalize this string
        "new_category_name": "New_test_category"
    })
    response = requests.post(f"{api_url}/products/post_new_user_product", data=data, headers=headers)
    assert response.status_code == 200
    assert response.json()['answer'] == 'New Product has been created'

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/products/{user_id}", headers=headers)
    assert response.status_code == 200

    user_products_with_new_product = default_user_products
    user_products_with_new_product['New_test_category'] = {'ico': 'test_ico', 'color': 'test_color',
                                                           'products': ['New_test_product']}
    print(user_products_with_new_product)
    print(response.json())
    assert response.json() == user_products_with_new_product


def test_update_user_product_with_new_name_user(api_url):
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "user_id": user_id,
        "old_category": "New_test_category",
        "new_category": "Other",
        "new_product_name": "very_new_test_product",
        "old_product_name": "New_test_product"
    })

    response = requests.put(f"{api_url}/products/update_user_product", data=data, headers=headers)
    assert response.status_code == 200
    print(response.json())
    assert response.json()[0] == "0 receipts were modified"


def test_update_user_product_with_old_name_user(api_url):
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "user_id": user_id,
        "old_category": "Other",
        "new_category": "New_test_category",
        "new_product_name": "very_new_test_product",
        "old_product_name": "very_new_test_product"
    })

    response = requests.put(f"{api_url}/products/update_user_product", data=data, headers=headers)
    assert response.status_code == 200
    print(response.json())
    assert response.json()[0] == "OK"


def test_update_user_product_with_wrong_user_id_admin(api_url):
    a_email = "nice.zdorik@gmail.com"
    a_password = ADMIN_PASS
    a_auth_response = requests.post(f"http://10.9.179.156:8080/token", "username=" + a_email + "&password=" + a_password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    a_payload = jwt.decode(a_auth_response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    a_user_id: int = payload.get("user_id")

    headers = {
        "Authorization": f"Bearer {a_auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "user_id": -1,
        "old_category": "Other",
        "new_category": "New_test_category",
        "new_product_name": "very_new_test_product",
        "old_product_name": "very_new_test_product"
    })

    response = requests.put(f"{api_url}/products/update_user_product", data=data, headers=headers)
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('Error') == f'There is no record with this user_id: {-1}'


def test_update_user_product_with_another_user_id_user(api_url):
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "user_id": 5,
        "old_category": "Other",
        "new_category": "New_test_category",
        "new_product_name": "very_new_test_product",
        "old_product_name": "very_new_test_product"
    })

    response = requests.put(f"{api_url}/products/update_user_product", data=data, headers=headers)
    assert response.status_code == 401
    print(response.json())
    assert response.json().get('detail') == 'You provided user_id of another user'


def test_delete_user_product_user(api_url):
    category_name = "New_test_category"
    product_name = "Very_new_test_product"
    print(user_id)
    query = f"?user_id={user_id}&category_name={category_name}&product_name={product_name}"
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
    }

    response = requests.delete(f"{api_url}/products/delete_user_product/{query}", headers=headers)
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('detail') == 'Success'


def test_delete_user_product_with_another_user_id_user(api_url):
    category_name = "New_test_category"
    product_name = "Very_new_test_product"
    query = f"?user_id=1&category_name={category_name}&product_name={product_name}"
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
    }

    response = requests.delete(f"{api_url}/products/delete_user_product/{query}", headers=headers)
    assert response.status_code == 401


def test_delete_user_category_user(api_url):
    category_name = "New_test_category"
    print(user_id)
    query = f"?user_id={user_id}&category_name={category_name}"
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
    }

    response = requests.delete(f"{api_url}/products/delete_user_category/{query}", headers=headers)
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('detail') == 1


def test_delete_user_category_with_another_user_id_user(api_url):
    category_name = "New_test_category"
    query = f"?user_id=1&category_name={category_name}"
    headers = {
        "Authorization": f"Bearer {auth_response.json()['access_token']}",
        'accept': 'application/json',
    }

    response = requests.delete(f"{api_url}/products/delete_user_category/{query}", headers=headers)
    assert response.status_code == 401
    assert response.json().get('detail') == 'You provided user_id of another user'
    delete_receipts(user_id)




# delete_product X
# delete_category X
# update_user_product X
# post_new_user_category X
# post_new_user_product X
# products/{user_id} X
