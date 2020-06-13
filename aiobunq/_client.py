import asyncio
import base64
import json
import os
import uuid
from contextlib import contextmanager
from typing import Iterable
from urllib.parse import urljoin

from aiohttp import ClientSession

from . import _auth as auth
from ._models import MonetaryAccount


__all__ = ["Client"]

URL_BUNQ_API_PROD = "https://api.bunq.com"
URL_BUNQ_API_SANDBOX = "https://public-api.sandbox.bunq.com"
URL_BUNQME_API = "https://api.bunq.me"
URL_CHECKOUT_API = "https://api.checkout.com"

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

BUNQME_URL_NAME = "EX4"
POST = "POST"
GET = "GET"
PUT = "PUT"


class Client:
    """
    Main client
    """

    ACCEPTED_METHODS = [POST, GET, PUT]
    SLASH = "/"
    DEFAULT_STORE_FP = os.path.join(os.path.expanduser("~"), "._~bunq.state")
    URI_MONETARY_ACCOUNT = "/".join(["user", "{}", "monetary-account", "{}"])


    @property
    def id(self):
        return self.basic_auth.id

    @property
    def headers(self):
        return {
            HDR_KEY_X_BUNQ_CLIENT_REQUEST_ID: str(uuid.uuid4()),
            HDR_KEY_X_BUNQ_GEOLOCATION: HDR_VAL_X_BUNQ_GEOLOCATION,
            HDR_KEY_X_BUNQ_LANGUAGE: HDR_VAL_X_BUNQ_LANGUAGE,
            HDR_KEY_X_BUNQ_REGION: HDR_VAL_X_BUNQ_REGION,
            HDR_KEY_CACHE_CONTROL: HDR_VAL_CACHE_CONTROL,
            HDR_KEY_USER_AGENT: HDR_VAL_USER_AGENT,
            HDR_KEY_ACCEPT_ENCODING: HDR_VAL_ACCEPT_ENCODING,
            HDR_KEY_ACCEPT: HDR_VAL_ACCEPT,
            HDR_KEY_CONNECTION: HDR_VAL_CONNECTION,
        }

    @property
    def base(self):
        if not self._base:
            self._base = "".join(
                (
                    URL_BUNQ_API_SANDBOX
                    if self.basic_auth.sandbox
                    else URL_BUNQ_API_PROD,
                    API_VERSION,
                )
            )
        return self._base

    @base.setter
    def base(self, value):
        self._base = value

    @contextmanager
    def foreign_base_url(self, url):
        try:
            self._base = url
            self.sign_requests = False
            yield
        except:
            raise
        finally:
            self._base = None
            self.sign_requests = True

    async def get_session(self):
        self._session = ClientSession(connector_owner=False)
        return self._session

    @property
    def session(self):
        return self._session

    @classmethod
    def restore(cls, filepath=None):
        filepath = filepath or cls.DEFAULT_STORE_FP
        basic_auth = auth.BasicAuth.load_file(filepath)
        return cls(basic_auth)

    @property
    def sign_requests(self):
        if self._sign_requests is False:
            return False
        elif not self.basic_auth.token:
            return False
        return True

    @sign_requests.setter
    def sign_requests(self, value):
        self._sign_requests = value

    def __init__(self, basic_auth: auth.BasicAuth = None):
        self.last_raw_response = None
        self.last_response = None
        self.last_request_info = None
        self.last_request = None
        self._session = None
        self._base = None
        # self._public_session = None
        self.basic_auth: auth.BasicAuth = basic_auth
        self.auth = None
        self._sign_requests = None
        self._initialize_auth()

    def save(self, filepath=None):
        filepath = filepath or self.DEFAULT_STORE_FP
        self.basic_auth.save_file(filepath)

    def _initialize_auth(self):
        if self.basic_auth.sandbox:
            print("Using sandbox environment")
        self.auth: auth.Auth = auth.Auth(self.basic_auth)


    async def logon(self):
        await self._install()
        await self._device_server()
        await self._session_server()
        await self.get_monetary_account()
        from ._bunqme import BunqMe
        self.bunq_me = BunqMe(self)


    async def _install(self):
        if self.basic_auth.sandbox:
            response = await self.request(POST, "sandbox-user",)
            self.basic_auth.api_key = response[0]["ApiKey"]["api_key"]

        response = await self.request(
            POST, URI_INSTALLATION, dict(client_public_key=self.basic_auth.public_key),
        )
        self.basic_auth.token = response[1]["Token"]["token"]
        self.basic_auth.public_key_peer = response[2]["ServerPublicKey"][
            "server_public_key"
        ]

    async def _device_server(self, permitted_ips: Iterable = ("*",)):
        response = await self.request(
            POST,
            URI_DEVICE_SERVER,
            dict(
                description="device",
                secret=self.basic_auth.api_key,
                permitted_ips=permitted_ips,
            ),
        )
        self.basic_auth.device_id = response[0]["Id"]["id"]

    async def _session_server(self):
        response = await self.request(
            POST, URI_SESSION_SERVER, dict(secret=self.basic_auth.api_key,)
        )
        self.basic_auth.session_token = response[1]["Token"]["token"]
        self.basic_auth._last_auth_timestamp = response[1]["Token"]["updated"]
        self.basic_auth.user = response[2]["UserPerson"]


    async def get_monetary_account(self):
        response = await self.request(
            GET, self.URI_MONETARY_ACCOUNT.format(self.basic_auth.id, "")
        )
        self.basic_auth.monetary_accounts = self.monetary_accounts = [
            MonetaryAccount(i) for i in response
        ]

    def _sign(self, body):
        return base64.b64encode(self.auth.sign(body)).decode()

    async def request(self, method, endpoint, data=None, headers=None, **kwargs):
        if not self._session:
            await self.get_session()

        endpoint = urljoin("/", endpoint)
        headers_ = headers or {}
        if self.sign_requests:
            headers_ = {
                HDR_KEY_X_BUNQ_CLIENT_SIGNATURE: self._sign(json.dumps(data).encode()),
                HDR_KEY_X_BUNQ_CLIENT_AUTH: self.basic_auth.session_token
                or self.basic_auth.token,
            }

        async with self.session.request(
            method,
            self.base + endpoint,
            json=data,
            headers={**self.headers, **headers_},
            **kwargs
        ) as r:
            self.last_raw_response = r
            self.last_request_info = r.request_info
            self.last_response = r = await r.json()
            try:
                return r["Response"]
            except KeyError:
                try:
                    return r["Error"]
                except KeyError:
                    pass
            return r

    # def __getattribute__(self, item):
    #     exc = None
    #     try:
    #         return object.__getattribute__(self, item)
    #     except AttributeError as e:
    #         exc = e
    #     try:
    #         if item.upper() in self.ACCEPTED_METHODS:
    #             def do_method(*a, **kw):
    #                 return self.request(item, *a, **kw)
    #             return do_method
    #         return object.__getattribute__(self.session, item)
    #     except Exception:
    #         pass
    #     try:
    #         return object.__getattribute__(self.basic_auth, item)
    #     except AttributeError:
    #         pass
    #     raise exc
    #
    # async def __aenter__(self):
    #     pass
    #
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #
    #     pass

    def __del__(self):
        if self._session:
            try:
                if asyncio.get_running_loop().is_running():
                    asyncio.create_task(self._session.close())
            except RuntimeError:
                asyncio.get_event_loop().run_until_complete(self._session.close())
