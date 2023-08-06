import requests
import jwt


# Main class
class AuthClient:
    def __init__(self, client_id, client_secret, code_redirect_uri, service_endpoint):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__code_redirect_uri = code_redirect_uri
        self.__auth_endpoint = f"{service_endpoint}/oauth/auth"
        self.__token_endpoint = f"{service_endpoint}/oauth/token"
        self.__register_endpoint = f"{service_endpoint}/oauth/register"

    def authorize_user(self, username, password):
        data = {
            "username": username,
            "password": password,
            "client_id": self.__client_id,
            "response_type": "code",
            "redirect_uri": self.__code_redirect_uri,
        }

        response = requests.post(self.__auth_endpoint, data=data)
        return response.json(), response.status_code

    def get_tokens(self, code):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "redirect_uri": self.__code_redirect_uri,
        }

        response = requests.post(self.__token_endpoint, data=data)
        return response.json(), response.status_code

    def do_refresh(self, token):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret
        }
        response = requests.post(self.__token_endpoint, data=data)
        return response.json(), response.status_code

    def register(self, username, password):
        data = {
            "username": username,
            "password": password,
            "client_id": self.__client_id,
            "secret": self.__client_secret,
        }
        response = requests.post(self.__register_endpoint, data=data)
        return response.json(), response.status_code

    def decode(self, token):
        data = jwt.decode(token,  key=b"00000000", algorithms=["HS512"], audience=["client"])
        return data




