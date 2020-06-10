import base64
import json
import os
import uuid
from typing import Iterable
from urllib.parse import urljoin
from aiohttp import ClientSession
import asyncio
from . import _auth as auth

__all__ = ['Client']


class Client:
    URL_BUNQ_API_PROD = "https://api.bunq.com"
    URL_BUNQ_API_SANDBOX = "https://public-api.sandbox.bunq.com"

    API_VERSION = "/v1"
    URI_INSTALLATION = "/installation"
    URI_DEVICE_SERVER = "/device-server"
    URI_SESSION_SERVER = "/session-server"

    HDR_KEY_USER_AGENT = "User-Agent"
    HDR_VAL_USER_AGENT = "AIOBunq Client v1"

    HDR_KEY_CONNECTION = "Connection"
    HDR_VAL_CONNECTION = "Keep-Alive"

    HDR_KEY_ACCEPT = "Accept"
    HDR_VAL_ACCEPT = "*/*"

    HDR_KEY_ACCEPT_ENCODING = "Accept-Encoding"
    HDR_VAL_ACCEPT_ENCODING = ", ".join(("identity", "deflate"))

    HDR_KEY_X_BUNQ_CLIENT_AUTH = "X-Bunq-Client-Authentication"
    HDR_KEY_X_BUNQ_CLIENT_SIGNATURE = "X-Bunq-Client-Signature"
    HDR_KEY_X_BUNQ_SERVER_SIGNATURE = "X-Bunq-Server-Signature"
    HDR_KEY_X_BUNQ_CLIENT_REQUEST_ID = "X-Bunq-Client-Request-Id"
    HDR_KEY_X_BUNQ_GEOLOCATION = "X-Bunq-Geolocation"
    HDR_VAL_X_BUNQ_GEOLOCATION = "0 0 0 0 NL"
    HDR_KEY_X_BUNQ_REGION = "X-Bunq-Region"
    HDR_VAL_X_BUNQ_REGION = "en_US"
    HDR_KEY_X_BUNQ_LANGUAGE = "X-Bunq-Language"
    HDR_VAL_X_BUNQ_LANGUAGE = HDR_VAL_X_BUNQ_REGION
    HDR_KEY_CACHE_CONTROL = "Cache-Control"
    HDR_VAL_CACHE_CONTROL = "none"

    POST = "POST"
    GET = "GET"
    PUT = "PUT"

    ACCEPTED_METHODS = [POST,GET,PUT]

    SLASH = "/"

    DEFAULT_STORE_FP = os.path.join(
        os.path.expanduser('~'),
        '._~bunq.state'
    )


    @property
    def headers(self):
        return {
            self.HDR_KEY_X_BUNQ_CLIENT_REQUEST_ID: str(uuid.uuid4()),
            self.HDR_KEY_X_BUNQ_GEOLOCATION: self.HDR_VAL_X_BUNQ_GEOLOCATION,
            self.HDR_KEY_X_BUNQ_LANGUAGE: self.HDR_VAL_X_BUNQ_LANGUAGE,
            self.HDR_KEY_X_BUNQ_REGION: self.HDR_VAL_X_BUNQ_REGION,
            self.HDR_KEY_CACHE_CONTROL: self.HDR_VAL_CACHE_CONTROL,
            self.HDR_KEY_USER_AGENT: self.HDR_VAL_USER_AGENT,
            self.HDR_KEY_ACCEPT_ENCODING: self.HDR_VAL_ACCEPT_ENCODING,
            self.HDR_KEY_ACCEPT: self.HDR_VAL_ACCEPT,
            self.HDR_KEY_CONNECTION: self.HDR_VAL_CONNECTION,
        }


    @property
    def base(self):
        return "".join((self.URL_BUNQ_API_SANDBOX
                        if self.basic_auth.sandbox else self.URL_BUNQ_API_PROD,
                        self.API_VERSION))


    @property
    def session(self):
        if not self._session:
            self._session = ClientSession(connector_owner=False)
        return self._session


    @classmethod
    def restore(cls, filepath=DEFAULT_STORE_FP):
        basic_auth = auth.BasicAuth.load_file(filepath)
        return cls(basic_auth)


    def __init__(self, basic_auth: auth.BasicAuth = None):
        self.last_raw_response = None
        self.last_response = None
        self.last_request_info = None
        self.last_request = None
        self._session = None
        self.basic_auth: auth.BasicAuth = basic_auth
        self.auth = None
        self._initialize_auth()


    def save(self, filepath=DEFAULT_STORE_FP):
        self.basic_auth.save_file(filepath)


    def _initialize_auth(self):
        if self.basic_auth.sandbox:
            print('Using sandbox environment')
        self.auth: auth.Auth = auth.Auth(self.basic_auth)


    async def logon(self):
        await self._install()
        await self._device_server()
        await self._session_server()


    async def _install(self):
        response = await self.request(self.POST, self.URI_INSTALLATION, dict(
            client_public_key=self.basic_auth.public_key
        ))
        self.basic_auth.token = response[1]['Token']['token']
        self.basic_auth.public_key_peer = response[2]['ServerPublicKey']['server_public_key']


    async def _device_server(self, permitted_ips: Iterable = ("*",)):
        response = await self.request(self.POST, self.URI_DEVICE_SERVER, dict(
            description="device", secret=self.basic_auth.api_key,
            permitted_ips=permitted_ips
        ))
        self.basic_auth.device_id = response[0]['Id']['id']


    async def _session_server(self):
        response = await self.request(self.POST, self.URI_SESSION_SERVER, dict(
            secret=self.basic_auth.api_key,
        ))
        self.basic_auth.session_token = response[1]['Token']['token']
        self.basic_auth._last_auth_timestamp = response[1]['Token']['updated']
        self.basic_auth.user = response[2]['UserPerson']


    def _sign(self, body):
        return base64.b64encode(
            self.auth.sign(body)).decode()


    async def request(self, method, endpoint, data=None, **kwargs):

        endpoint = urljoin('/', endpoint)
        headers = (self.headers if not self.basic_auth.token
                   else {
                        self.HDR_KEY_X_BUNQ_CLIENT_SIGNATURE: self._sign(json.dumps(data).encode()),
                        self.HDR_KEY_X_BUNQ_CLIENT_AUTH: self.basic_auth.session_token or self.basic_auth.token,
                        **self.headers})
        r = await self.session.request(
            method,
            self.base + endpoint,
            json=data,
            headers=headers,
            **kwargs)
        self.last_raw_response = r
        self.last_request_info = r.request_info
        self.last_response = r = await r.json()
        try:
            return r['Response']
        except KeyError:
            raise Exception(str(r['Error']))
        except Exception:
            raise

    def __getattribute__(self, item):
        exc = None
        try:
            return object.__getattribute__(self, item)
        except AttributeError as e:
            exc = e
        try:
            if item.upper() in self.ACCEPTED_METHODS:
                def do_method(*a, **kw):
                    return self.request(item, *a, **kw)
                return do_method
            return object.__getattribute__(self.session, item)
        except AttributeError:
            pass
        try:
            return object.__getattribute__(self.basic_auth, item)
        except AttributeError:
            pass
        raise exc

#
#
# class Bunq(object):
#
#     URL_BUNQ_API_VERSION = "/v1"
#     URL_BUNQ_API_PROD = "https://api.bunq.com"
#     URL_BUNQ_API_SANDBOX = "https://public-api.sandbox.bunq.com"
#
#
#     ENDPOINT_INSTALLATION = "/installation"
#     ENDPOINT_DEVICE_SERVER = "/device-server"
#     ENDPOOINT_SESSION = "/"
#
#     ERR_WRONG_SIGNATURE = 'server sent wrong signature for content. signature: {raw_sig}'
#
#
#     async def install(self):
#         # if not self.session:
#         pass
