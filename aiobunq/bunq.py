import asyncio
import logging
import string
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from json import JSONEncoder, JSONDecoder
from uuid import uuid4

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from aiohttp import ClientSession, TCPConnector, ClientTimeout, ClientResponse

from .util import FormatterSkipKeywordNotFound

__ALL__ = ["Bunq"]


class BunqApiResponseError(BaseException):
    pass


class Bunq(object):
    """
    Async Bunq Api
    """

    def __init__(self, api_key=False, rsa_bits=2048, debug=False):
        """
        todo: docu
        :param api_key:
        :param rsa_bits:
        :param debug:
        """
        self.sandbox = not api_key
        self.private_key = None
        self.public_key = None
        self.public_key_remote = None
        self.is_installed = False
        self.user_person = {}
        self.monetary_accounts: list = []
        self.current_monetary_account = None
        self.is_session_established = False
        self.token = None
        self.api_key = api_key
        self.last_request = None
        self.last_response = None

        self._base = None
        self._rng = None
        self.rsa_bits = rsa_bits
        self.debug = debug
        self.session = None
        self.logger = logging.getLogger(f"Bunq Api {hex(id(self))}")
        self._jsonencoder = JSONEncoder()
        self._jsondecoder = JSONDecoder()
        self._connection = None
        self._executor = ThreadPoolExecutor()
        self._accepted_methods = ["GET", "PUT", "POST"]
        self._strfmt = FormatterSkipKeywordNotFound()
        self.active_monetary_account_id = "not_authenticated"

        
    @property
    def base_url(self):
        """
        returns the api base url

        :return:
        """
        if not self._base:
            self._base = (
                "https://api.bunq.com/v1/"
                if not self.sandbox
                else "https://public-api.sandbox.bunq.com/v1/"
            )
        return self._base

    
    
    def _create_headers(self, **headers):
        """
        Creates bunq request headers from a supplied (or not) headers mapping

        :param headers: headers
        :type headers: (dict, Mapping)
        :return:
        """
        _hdrs = {
            "X-Bunq-Client-Request-Id": str(uuid4()),
            "X-Bunq-Geolocation": "0 0 0 0 NL",
            "X-Bunq-Language": "en_US",
            "X-Bunq-Region": "en_US",
            "Cache-Control": "none",
            "User-Agent": "AioBunq Python Api",
        }
        headers.update(_hdrs)
        return headers

    
    
    async def install(self):
        """
        Creates a session context

        :return:
        """

        if self.is_installed:
            return

        if not self.sandbox and not self.api_key:
            raise Exception("in production, you have to provide the api_key manually")

        def create_keys():
            key = RSA.generate(self.rsa_bits)
            self.public_key, self.private_key = key.publickey(), key
            self._rng = Random.new()

        await asyncio.get_running_loop().run_in_executor(self._executor, create_keys)

        if not self._connection:
            self._connection = ClientSession(
                connector=TCPConnector(), timeout=ClientTimeout(5.0)
            )

        if self.sandbox:
            response = await self.call("POST", "sandbox-user")
            self.api_key = response[0]["ApiKey"]["api_key"]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # step 1 - installation
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        req_data = {"client_public_key": self.public_key.export_key("PEM").decode()}
        response = await self.call("POST", "installation", req_data)
        self.token = response[1]["Token"]["token"]
        self.public_key_remote = response[2]["ServerPublicKey"]["server_public_key"]
        self.is_installed = True

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # step 2 - Device-Server
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        req_data = {
            "description": "hiii",
            "secret": self.api_key,
            "permitted_ips": ["*"],
        }
        await self.call("POST", "device-server", req_data)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # step 3 - Session-Server
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        req_data = {"secret": self.api_key}
        response = await self.call("POST", "session-server", req_data)
        self.token = response[1]["Token"]["token"]
        self.user_person = response[2]["UserPerson"]
        self.user_id = self.user_person["id"]

        self.is_session_established = True

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # step 4 - Extra initialization
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        await self.refreshMonetaryAccounts()

        self.active_monetary_account_id = self.monetary_accounts[0]["id"]

        await self.refreshIdealIssuers()

        
        
    async def refreshIdealIssuers(self):
        """

        :return:
        """
        response = self.ideal_issuers = await self._connection.get(
            "https://api.bunq.me/v1/bunqme-merchant-directory-ideal",
            headers=self._create_headers(),
        )
        response = await response.json()
        self.ideal_issuers = response["Response"][0]["IdealDirectory"]["country"][0][
            "issuer"
        ]

        
        
    async def refreshMonetaryAccounts(self):
        response = await self.call("GET", f"user/{self.user_id}/monetary-account")
        self.monetary_accounts = [r["MonetaryAccountBank"] for r in response]

    @property
    def active_monetary_account(self):
        """

        :return:
        """
        for ma in self.monetary_accounts:
            if ma["id"] == self.active_monetary_account_id:
                return ma

            
            
    def setActiveMonetaryAccount(self, id):
        """
        Sets the active monetary account id used in calls

        :param id: monetary_account_id or index of active_monetary_accounts

        """
        for ma in self.monetary_accounts:
            if ma["id"] == id:
                self.active_monetary_account_id = ma["id"]
                break
        else:
            self.active_monetary_account_id = self.monetary_accounts[id]["id"]

            
            
    async def call(self, method, endpoint, data=None, **params):
        """

        :param method:
        :param endpoint:
        :param data:
        :param params:
        :return:
        """

        if not self.is_installed and not any(
            map(lambda word: word in endpoint, ("installation", "sandbox-user"))
        ):

            raise Exception(
                "a call to install() should be made first to setup the api context"
            )

        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        if "{userID}" in endpoint:
            endpoint = self._strfmt.format(endpoint, **{"userID": self.user_id})
        if "{monetary-accountID}" in endpoint:
            endpoint = self._strfmt.format(
                endpoint, **{"monetary-accountID": self.active_monetary_account_id}
            )

        url = self.base_url + endpoint
        headers = self._create_headers()
        body = self._jsonencoder.encode(data or {})
        if self.is_installed:
            signer = PKCS1_v1_5.new(self.private_key)
            digest = SHA256.new()
            digest.update(body.encode())
            sig = signer.sign(digest)
            headers.update(
                {
                    "X-Bunq-Client-Authentication": self.token,
                    "X-Bunq-Client-Signature": b64encode(sig).decode(),
                }
            )

        async with self._connection.request(
            method, url, data=body, params=params, headers=headers
        ) as response:
            return await self._check_response(response)
            # return await response.json()

            
            
    async def _check_response(self, response: ClientResponse):
        """

        :param response:
        :return:
        """
        self.logger.debug("REQUEST: {0.status} {0.method} {0.url}".format(response))
        self.last_response = response
        self.last_request = response.request_info
        if response.method not in ("GET", "POST", "PUT", "DELETE"):
            return await response.text()
        try:
            data = await response.json()
        except Exception as e:
            raise BunqApiResponseError(f"{e} {await response.read()}")
        self.logger.debug(f"RESPONSE: {data}\n\n")
        try:
            return data["Response"]
        except KeyError as e:
            raise BunqApiResponseError(data["Error"])
        except:
            raise

            
            
    async def getBunqMeTabs(self):
        pass

    
    
    async def createBunqMeIdealRequest(
        self,
        value,
        currency="EUR",
        description="",
        redirect_url="",
        ideal_issuer_bic="",
    ):
        """
        Create a payment request with value, currency, description, redirect_url, and issuer_bic and
        returns a dict containing the the Bunqme-Tab and direct iDeal payment link.
        This also triggers notifications for category BUNQME_TAB so you can receive webhook/ipn
        responses from Bunq when subscribed.

        :param value:
        :param currency:
        :param description:
        :param redirect_url:
        :param ideal_issuer_bic:
        :return: dict

        EXAMPLE RESPONSE
        {
            'uuid': 'SOME-UUID-STRING',
            'status': 'PAYMENT_CREATED',
            'issuer_authentication_url': 'https://r.girogate.de/pi/bunqideal?tx=630520405&rs=S6j435andmanymore',
            'bunqme_type': 'TAB',
            'bunqme_uuid': 'SOME-OTHER-UUID-STRING'
        }

        """
        reqdata = {
            "bunqme_tab_entry": {
                "amount_inquired": {"value": value, "currency": currency},
                "description": description,
                "redirect_url": redirect_url,
            }
        }
        response = await self.call(
            "POST",
            "user/{userID}/monetary-account/{monetary-accountID}/bunqme-tab",
            reqdata,
        )
        tab_id = response[0]["Id"]["id"]

        response = await self.get(
            "user/{userID}/monetary-account/{monetary-accountID}/bunqme-tab/"
            + str(tab_id)
        )
        bunqme_tab_uuid = response[0]["BunqMeTab"]["bunqme_tab_entry"]["uuid"]

        reqdata = {
            "amount_requested": {"currency": currency, "value": value,},
            "bunqme_type": "TAB",
            "issuer": ideal_issuer_bic,
            "merchant_type": "IDEAL",
            "bunqme_uuid": bunqme_tab_uuid,
        }

        # change to bunq.me api base url
        self._base = "https://api.bunq.me/v1/"

        response = await self.call("POST", "bunqme-merchant-request", reqdata)
        bunqme_merchant_request_uuid = response[0]["BunqMeMerchantRequest"]["uuid"]

        while True:
            await asyncio.sleep(0.5)
            response = await self.call(
                "GET", "bunqme-merchant-request/" + bunqme_merchant_request_uuid
            )
            if (
                response[0]["BunqMeMerchantRequest"]["status"]
                == "PAYMENT_WAITING_FOR_CREATION"
            ):
                continue
            # reset api url to main bunq.com api instead of bunq.me api
            self._base = None
            return response[0]["BunqMeMerchantRequest"]

        
        
    async def checkOpenBunqMeIdealRequests(self):
        """

        :return:
        """
        # idea: search by description

        response = await self.call(
            "GET", "/user/{userID}/monetary-account/{monetary-accountID}/bunqme-tab"
        )

        answer = []
        for bunq_me_tab in response:
            bunq_me_tab = bunq_me_tab["BunqMeTab"]
            bunq_me_tab_entry = bunq_me_tab["bunqme_tab_entry"]
            description = bunq_me_tab_entry["description"]
            inquiries = bunq_me_tab["result_inquiries"]
            amount_inquired = float(bunq_me_tab_entry["amount_inquired"]["value"])
            currency = bunq_me_tab_entry["amount_inquired"]["currency"]
            total_payment_value = 0.0

            if inquiries and len(inquiries) > 0:
                for inquiry in inquiries:
                    payment = inquiry["payment"]["Payment"]
                    payment_amount = payment["amount"]["value"]
                    payment_amount = float(payment_amount)
                    total_payment_value += payment_amount

            answer += [
                {
                    "currency": currency,
                    "description": description,
                    "amount_paid": total_payment_value,
                    "amount_inquired": amount_inquired,
                    "bunqme_tab_id": bunq_me_tab["id"],
                }
            ]

        return answer

    
    
    def __repr__(self):
        r = "<Bunq Api (installed: {}, session: {}, active_monetary_account: {})>"
        return r.format(
            self.is_installed,
            self.is_session_established,
            self.active_monetary_account_id,
        )

    
    
    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if attr.upper() in self._accepted_methods:
                return partial(self.call, attr)
            raise

