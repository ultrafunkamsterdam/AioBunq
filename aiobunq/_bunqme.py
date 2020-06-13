import asyncio
import base64
import json
from contextlib import contextmanager

from ._models import BunqObject, BunqMeMerchantRequest
from ._client import Client


BUNQME_URL_NAME = "EX4"  #change to 0
KEY_BUNQME_CHECKOUT_PUBKEY = "pk_42a4efb8-cee1-4748-9e4e-06bf7174ca81"
URL_BUNQME_API = "https://api.bunq.me"
URL_CHECKOUT_API = "https://api.checkout.com"
USER = "user"
URI_CHECKOUT_TOKENS = "/tokens"
VERSION = "v1"
TAB = "bunqme-tab"
TAB_ENTRY = "bunqme_tab_entry"
AMOUNT_INQUIRED = "amount_inquired"
AMOUNT_REQUESTED = "amount_requested"
MONETARY_ACCOUNT = "monetary-account"
MERCHANT_REQUEST = "bunqme-merchant-request"
CURRENCY = "currency"
ISSUER = "issuer"
BUNQME_UUID = "bunqme_uuid"
MERCHANT_TYPE = "merchant_type"
IDEAL = "IDEAL"
SOFORT = "SOFORT"
FUNDRAISER = "FUNDRAISER"
VALUE = "value"
BANCONTACT = "BANCONTACT"
BUNQME_TYPE = "bunqme_type"
POST = "POST"
URI_MONETARY_ACCOUNT = "/".join([USER, "{}", MONETARY_ACCOUNT, "{}"])


def set_bunqme_name(name):
    global BUNQME_URL_NAME
    BUNQME_URL_NAME = name


class BunqMe:
    @classmethod
    def add_to(cls, client: Client):
        client.bunqme = cls(client)
        return client

    # KEY_BUNQME_CHECKOUT_PUBKEY = "pk_42a4efb8-cee1-4748-9e4e-06bf7174ca81"
    # URL_BUNQME_API = "https://api.bunq.me"
    # URL_CHECKOUT_API = "https://api.checkout.com"
    # USER = "user"
    # URI_CHECKOUT_TOKENS = "/tokens"
    # VERSION = "v1"
    # TAB = "bunqme-tab"
    # TAB_ENTRY = "bunqme_tab_entry"
    # AMOUNT_INQUIRED = "amount_inquired"
    # AMOUNT_REQUESTED = "amount_requested"
    # MONETARY_ACCOUNT = "monetary-account"
    # MERCHANT_REQUEST = "bunqme-merchant-request"
    # CURRENCY = "currency"
    # ISSUER = "issuer"
    # BUNQME_UUID = "bunqme_uuid"
    # MERCHANT_TYPE = "merchant_type"
    # IDEAL = "IDEAL"
    # SOFORT = "SOFORT"
    # BUNQME_TYPE = "bunqme_type"
    # FUNDRAISER = "FUNDRAISER"
    # VALUE = "value"
    # BANCONTACT = "BANCONTACT"
    # URI_MONETARY_ACCOUNT = "/".join([USER, "{}", MONETARY_ACCOUNT, "{}"])

    def __init__(self, client: Client):
        self.client = client
        if client.monetary_accounts and len(client.monetary_accounts) > 0:
            self.set_current_account(client.monetary_accounts[0])
        else:
            raise Exception(
                "u have to have a minimum of 1 monetary account to use bunqme services"
            )

    @property
    def current_account(self):
        return self._monetary_account

    @current_account.setter
    def current_account(self, value):
        self._monetary_account = value

    def set_current_account(self, account):
        self.current_account = account

    async def getMonetaryAccounts(self):
        return await self.client.get(URI_MONETARY_ACCOUNT.format(self.client.id, ""))

    async def createTab(
        self,
        value: str = "",
        currency: str = "EUR",
        description: str = "",
        redirect_url: str = "",
    ):
        """Creates a Tab. Needed as base for all other payment options

        :param value:
        :param currency:
        :param description:
        :param redirect_url:
        :return:[...,BunqObject,...]
        """
        r = await self.client.request(
            "POST",
            f"/user/{self.client.id}/monetary-account/{self.current_account.id}/bunqme-tab",
            data={
                TAB_ENTRY: {
                    AMOUNT_INQUIRED: {VALUE: value, CURRENCY: currency},
                    "description": description,
                    "redirect_url": redirect_url,
                }
            },
        )
        rid = r[0]["Id"]["id"]
        r = await self.client.request(
            "GET",
            f"/user/{self.client.id}/monetary-account/{self.current_account.id}/bunqme-tab/{rid}",
        )
        return [BunqObject(o) for o in r]



    async def createBunqMeIdeal(
        self,
        value: str = "",
        currency: str = "EUR",
        description: str = "",
        redirect_url: str = "",
        issuer_bic: str = None,
    ):
        """ Creates a request for an iDeal transaction.

        :param value:
        :param currency:
        :param description:
        :param redirect_url:
        :param issuer_bic:
        :return: list[dict]
        """
        if issuer_bic is None:
            raise KeyError(
                "issuer_bic is required for iDeal. Example BIC of Abn-Amro: ABNANL2A"
            )
        tab = await self.createTab(value, currency, description, redirect_url)
        tab_uuid = tab[0].bunqme_tab_entry["uuid"]

        with self.client.foreign_base_url("/".join([URL_BUNQME_API,VERSION])):
            response = await self.client.request(
                POST,
                MERCHANT_REQUEST,
                data={
                    AMOUNT_REQUESTED: {CURRENCY: currency, VALUE: value,},
                    BUNQME_TYPE: "TAB",
                    MERCHANT_TYPE: IDEAL,
                    ISSUER: issuer_bic,
                    BUNQME_UUID: tab_uuid,
                },
            )
            merchant_req_uuid = response[0]["BunqMeMerchantRequest"]["uuid"]
            while True:
                await asyncio.sleep(0.5)
                res = await self.client.request(
                    "GET", MERCHANT_REQUEST + "/" + merchant_req_uuid
                )
                merchant_request = res[0]["BunqMeMerchantRequest"]
                if (
                    merchant_request["issuer_authentication_url"] is not None
                    and merchant_request["status"] == "PAYMENT_CREATED"
                ):
                    merchant_request = BunqMeMerchantRequest(*merchant_request)
                    merchant_request.client = self.client
                    return merchant_request



    async def createBunqMeSofort(
        self,
        value: str = "",
        currency: str = "EUR",
        description: str = "",
        redirect_url: str = "",
    ):
        """ Creates a request for a Sofort transaction.

        :param value:
        :param currency:
        :param description:
        :param redirect_url:
        :param issuer_bic:
        :return: list[dict]
        """
        tab = await self.createTab(value, currency, description, redirect_url)
        tab_uuid = tab[0].bunqme_tab_entry["uuid"]

        with self.client.foreign_base_url("/".join([URL_BUNQME_API,VERSION])):

            response = await self.client.request(
                POST,
                MERCHANT_REQUEST,
                data={
                    AMOUNT_REQUESTED: {CURRENCY: currency, VALUE: value,},
                    BUNQME_TYPE: "TAB",
                    MERCHANT_TYPE: SOFORT,
                    BUNQME_UUID: tab_uuid,
                },
            )
            merchant_req_uuid = response[0]["BunqMeMerchantRequest"]["uuid"]
            while True:
                await asyncio.sleep(0.5)
                res = await self.client.request(
                    "GET", MERCHANT_REQUEST + "/" + merchant_req_uuid
                )
                merchant_request = res[0]["BunqMeMerchantRequest"]
                if (
                    merchant_request["issuer_authentication_url"] is not None
                    and merchant_request["status"] == "PAYMENT_CREATED"
                ):
                    merchant_request._request = BunqMeMerchantRequest(*merchant_request)
                    merchant_request.client = self.client
                    return merchant_request


    async def createBunqMeBancontact(
        self,
        value: str = "",
        currency: str = "EUR",
        description: str = "",
        redirect_url: str = "",
        name="Naam",
    ):
        """Creates a request for a Sofort transaction.

        Args:
            value:
            currency:
            description:
            redirect_url:

        Returns:
        """
        tab = await self.createTab(value, currency, description, redirect_url)
        tab_uuid = tab[0].bunqme_tab_entry["uuid"]

        with self.client.foreign_base_url("/".join([URL_BUNQME_API,VERSION])):

            response = await self.client.request(
                POST,
                MERCHANT_REQUEST,
                data={
                    AMOUNT_REQUESTED: {CURRENCY: currency, VALUE: value,},
                    BUNQME_TYPE: "TAB",
                    MERCHANT_TYPE: BANCONTACT,
                    BUNQME_UUID: tab_uuid,
                    "name": name,
                },
            )
            merchant_req_uuid = response[0]["BunqMeMerchantRequest"]["uuid"]
            while True:
                await asyncio.sleep(0.5)

                res = await self.client.request(
                    "GET", MERCHANT_REQUEST + "/" + merchant_req_uuid
                )
                merchant_request = res[0]["BunqMeMerchantRequest"]
                if (
                    merchant_request["issuer_authentication_url"] is not None
                    and merchant_request["status"] == "PAYMENT_CREATED"
                ):

                    return BunqMeMerchantRequest(*merchant_request)


    async def createBunqMeCreditCard(
        self,
        value: str = "",
        currency: str = "EUR",
        description: str = "",
        redirect_url: str = "",
        name="",
        number="",
        expiry_month=0,
        expiry_year=2020,
        cvc="",
    ):

        with self.client.foreign_base_url(URL_CHECKOUT_API):
            response = await self.client.request(
                "POST",
                "/tokens",
                data={
                    "type": "card",
                    "number": number,
                    "expiry_month": expiry_month,
                    "expiry_year": expiry_year,
                    "cvv": cvc,
                    "name": name,
                    "phone": {},
                    "requestSource": "JS",
                },
                headers={
                    "content-type": "application/json",
                    "AUTHORIZATION": KEY_BUNQME_CHECKOUT_PUBKEY,
                },
            )
            if response.get("error_codes"):
                return response

            card_payment_token_data = base64.b64encode(
                json.dumps(response).encode()
            ).decode()

        with self.client.foreign_base_url("/".join([URL_BUNQME_API,VERSION])):

            fr_profile = await self.client.request(
                    "POST",
                    "bunqme-fundraiser-profile",
                    {"pointer": {
                         "type": "URL",
                        "value": f"https://bunq.me/{BUNQME_URL_NAME}"}
                    },
                )

            response = await self.client.request(
                "POST",
                "bunqme-merchant-request",
                data={
                    "amount_requested": {
                        "currency": str(currency),
                        "value": str(value),
                    },
                    "merchant_type": "CHECKOUT",
                    "bunqme_type": "FUNDRAISER",
                    "bunqme_uuid": fr_profile[0]['BunqMeFundraiserProfile']['uuid'],
                    "card_payment_token_data": card_payment_token_data,
                    "description": description,
                },
            )
            merchant_request_uuid = response[0]["BunqMeMerchantRequest"]['uuid']
            while True:
                await asyncio.sleep(0.25)
                response = await self.client.request(
                        "GET", "bunqme-merchant-request" + "/" + merchant_request_uuid
                    )
                merchant_request = response[0]['BunqMeMerchantRequest']
                if merchant_request['status'] != "PAYMENT_WAITING_FOR_CREATION":
                    r = BunqMeMerchantRequest(*response)
                    r.client = self.client
                    return r



class MerchantRequestWatcher:

    _store: set = set()
    _cbs: set = set()
    _client: Client = None

    @classmethod
    def add(cls, obj: BunqMeMerchantRequest):
        cls._store.add(obj)

    @classmethod
    def set_client(cls, client:Client):
        cls._client = client

    @classmethod
    def add_callback(cls, fn):
        cls._cbs.add(fn)

    @classmethod
    async def run(cls):
        with cls._client.foreign_base_url('/'.join([URL_BUNQME_API, VERSION, MERCHANT_REQUEST])):
            while True:
                try:
                    item = cls._store.pop()
                except IndexError:
                    await asyncio.sleep(2)
                    continue
                updated = BunqMeMerchantRequest(* (await cls._client.request('GET', item.uuid))[0] )
                if updated.status != 'PAYMENT_CREATED':
                    for callback in cls._cbs:
                        callback(updated)

