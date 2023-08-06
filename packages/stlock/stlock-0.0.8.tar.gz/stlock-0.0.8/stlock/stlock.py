import requests
import jwt


# Main class
class AuthClient:
    def __init__(self, client_id: str, client_secret: str, code_redirect_uri: str, service_endpoint: str):
        """
        Settings for authorization service
        :param client_id: client id
        :param client_secret: client secret
        :param code_redirect_uri: local redirection url
        :param service_endpoint: endpoint where authorization service exists
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__code_redirect_uri = code_redirect_uri
        self.__auth_endpoint = f"{service_endpoint}/oauth/auth"
        self.__token_endpoint = f"{service_endpoint}/oauth/token"
        self.__register_endpoint = f"{service_endpoint}/oauth/register"

    def authorize_user(self, username: str, password: str) -> (dict, int):
        """
        :param username: string username
        :param password: strign password
        :return:
        dict response with user tokens and token lifetime,
        int status code from auth service
        """
        data = {
            "username": username,
            "password": password,
            "client_id": self.__client_id,
            "response_type": "code",
            "redirect_uri": self.__code_redirect_uri,
        }

        response = requests.post(self.__auth_endpoint, data=data)
        return response.json(), response.status_code

    def get_tokens(self, code: str) -> (dict, int):
        """
        :param code: str authorization code for get access to the service
        :return:
        dict status of the response,
        int status code from auth service
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "redirect_uri": self.__code_redirect_uri,
        }

        response = requests.post(self.__token_endpoint, data=data)
        return response.json(), response.status_code

    def do_refresh(self, token: str) -> (dict, int):
        """
        :param token: str Refresh token
        :return:
        dict params tokens and token lifetime,
        int status code from auth service
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret
        }
        response = requests.post(self.__token_endpoint, data=data)
        return response.json(), response.status_code

    def register(self, username: str, password: str) -> (dict, int):
        """
        :param username: string username
        :param password: strign password
        :return:
        dict response from auth service,
        int status code from auth service
        """
        data = {
            "username": username,
            "password": password,
            "client_id": self.__client_id,
            "secret": self.__client_secret,
        }
        response = requests.post(self.__register_endpoint, data=data)
        return response.json(), response.status_code

    def decode(self, token) -> dict:
        """
        Decode token to get user info
        :param token: str access token
        :return:
        dict user info in token
        """
        data = jwt.decode(token,  key=b"00000000", algorithms=["HS512"], audience=["client"])
        return data




