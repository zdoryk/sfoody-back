import pytest
import requests

from env_variables import SECRET_KEY, ALGORITHM, ADMIN_PASS


@pytest.fixture
def api_url():
    return "http://10.9.179.156:8080"


def test_get_products_of_all_users_with_jwt_token_user(api_url):
    email = 'cypress@gmail.com'
    password = 'cypress'
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_products_of_all_users", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 401

    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info["detail"] == "Not enough permissions"


def test_get_receipts_of_all_users_with_jwt_token_user(api_url):
    email = 'cypress@gmail.com'
    password = 'cypress'
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_receipts_of_all_users", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 401

    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info["detail"] == "Not enough permissions"


def test_get_all_user_data_with_jwt_token_user(api_url):
    email = 'cypress@gmail.com'
    password = 'cypress'
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_all_user_data/5", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 401

    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info["detail"] == "Not enough permissions"

    info_response = requests.get(f"{api_url}/admin/get_all_user_data/1", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 401

    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info["detail"] == "You provided user_id of another user"


def test_get_receipts_of_all_users_with_jwt_token_admin(api_url):
    email = 'nice.zdorik@gmail.com'
    password = ADMIN_PASS
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_receipts_of_all_users", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 200
    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info[0] == {'user_id': 1, 'receipt_id': 1, 'createdAt': 1644231861,
                       'products': [{'product_name': 'apple', 'price': 10.01}], 'total_price': 10.01}


def test_get_products_of_all_users_with_jwt_token_admin(api_url):
    email = 'nice.zdorik@gmail.com'
    password = ADMIN_PASS
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_products_of_all_users", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 200
    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info[0] == {
        "Fruits": {
            "ico": "apple",
            "color": "#FF7043",
            "products": [
                "Apples",
                "Strawberry",
                "Pineapple",
                "Bananas"
            ]
        },
        "Meat": {
            "ico": "drumstick",
            "color": "#FF5252",
            "products": [
                "Beef",
                "Ham",
                "Pork"
            ]
        },
        "Drinks": {
            "ico": "drinks",
            "color": "#536DFE",
            "products": [
                "Juice"
            ]
        },
        "Semi-finished products": {
            "ico": "pizza",
            "color": "#B388FF",
            "products": [
                "Lasagne",
                "Beef pizza"
            ]
        },
        "Snacks": {
            "ico": "candy",
            "color": "#FFA726",
            "products": [
                "Snickers"
            ]
        },
        "Other": {
            "ico": "questionCircle",
            "color": "grey",
            "products": [
                "prikol",
                "Some really long product name",
                "Candy"
            ]
        },
        "Fish": {
            "ico": "fish",
            "color": "#F178B6",
            "products": [
                "Tuna"
            ]
        },
        "user_id": "1"
    }


def test_get_all_user_data_with_jwt_token_admin(api_url):
    email = 'nice.zdorik@gmail.com'
    password = ADMIN_PASS
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    info_response = requests.get(f"{api_url}/admin/get_all_user_data/5", headers=headers)

    # Assert that the request was successful
    assert info_response.status_code == 200
    # Assert that the information returned is what you expected
    info = info_response.json()
    assert info == {
        "categories": {
            "user_id": 5,
            "New": {
                "color": "string",
                "ico": "string",
                "products": [
                    "string"
                ]
            }
        },
        "receipts": [
            {
                "user_id": 5,
                "receipt_id": 1,
                "createdAt": 1670881286,
                "total_price": 19.41,
                "products": [
                    {
                        "product_name": "Apple",
                        "price": 2.59
                    },
                    {
                        "product_name": "Corn",
                        "price": 3.95
                    },
                    {
                        "product_name": "Beef",
                        "price": 10.59
                    },
                    {
                        "product_name": "Snickers",
                        "price": 0.99
                    },
                    {
                        "product_name": "Rice",
                        "price": 1.29
                    }
                ]
            },
            {
                "user_id": 5,
                "receipt_id": 2,
                "createdAt": 1670881296,
                "total_price": 19.41,
                "products": [
                    {
                        "product_name": "Apple",
                        "price": 2.59
                    },
                    {
                        "product_name": "Corn",
                        "price": 3.95
                    },
                    {
                        "product_name": "Beef",
                        "price": 10.59
                    },
                    {
                        "product_name": "Snickers",
                        "price": 0.99
                    },
                    {
                        "product_name": "Rice",
                        "price": 1.29
                    }
                ]
            }
        ],
        "new_user": False
    }

