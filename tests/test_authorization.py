from jose import jwt
import pytest
import requests

from env_variables import SECRET_KEY, ALGORITHM, DEFAULT_USER_CATEGORIES


@pytest.fixture
def api_url():
    return "http://10.9.179.156:8080"


def test_login(api_url):
    # Send a request to the API's authentication endpoint
    email = 'cypress@gmail.com'
    password = 'cypress'
    auth_response = requests.post(f"{api_url}/token", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    print(auth_response.json())
    payload = jwt.decode(auth_response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    email: str = payload.get("sub")
    currency: int = payload.get("currency")
    user_id: int = payload.get("user_id")
    token_scope: str = payload.get("scope")

    # Decode the JWT token to get the information you need
    # decoded_token = jwt.decode(jwt_token, verify=False)
    assert email == "cypress@gmail.com"
    assert user_id == 5
    assert token_scope == "user"
    assert currency == "USD"


def test_sign_up(api_url):
    # Send a request to the API's authentication endpoint
    email = 'new_user_test@gmail.com'
    password = 'NewTest111'
    auth_response = requests.post(f"{api_url}/token/register", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    print(auth_response.json())
    payload = jwt.decode(auth_response.json()['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    email: str = payload.get("sub")
    currency: int = payload.get("currency")
    user_id: int = payload.get("user_id")
    token_scope: str = payload.get("scope")

    # Decode the JWT token to get the information you need
    # decoded_token = jwt.decode(jwt_token, verify=False)
    assert email == "new_user_test@gmail.com"
    assert token_scope == "user"
    assert currency == "USD"

    headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
    response = requests.get(f"{api_url}/products/{user_id}", headers=headers)
    assert response.status_code == 200

    for_assert = DEFAULT_USER_CATEGORIES
    for_assert['user_id'] = user_id

    assert response.json() == for_assert


def test_sign_up_with_existing_email(api_url):
    # Send a request to the API's authentication endpoint
    email = 'new_user_test@gmail.com'
    password = 'NewTest111'
    auth_response = requests.post(f"{api_url}/token/register", "username=" + email + "&password=" + password,
                                  headers={'Content-Type': 'application/x-www-form-urlencoded'})

    assert auth_response.status_code == 409
    assert auth_response.json().get('detail') == "There is a user with same email"
