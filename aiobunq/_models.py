# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# part of aiobunq package
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def _undunder_dict(d):
    return {k: v for (k, v) in d.items() if not k[0] == "_"}


class BunqObject(object):


    # todo: ugly, tidy it up
    def __init__(self, o: dict, **kw):
        self._type, data = o.copy().popitem()
        self.__dict__.update(data)
        self.__dict__.update(kw)


    def __getitem__(self, item):
        return self.__dict__.get(item)


    def __setitem__(self, key, value):
        self.__dict__[key] = value


    def __iter__(self):
        from ._client import Client

        iters = dict((x, y)
                     for x, y in self.__dict__.items()
                     if not callable(y)
                     and not isinstance(y, (BunqObject, Client))
                     and not x.startswith('_'))
        for k, v in iters.items():
            yield k, v


    @property
    def dict(self):
        return dict(self)


    def __repr__(self):
        return f"<[{self._type}]({_undunder_dict(self.__dict__)})>"


class MonetaryAccount(BunqObject):
    # todo: ugly, tidy it up
    def __repr__(self):
        for item in self.alias:
            if item.get("type") == "IBAN":
                iban = item["value"]
        return "<[{0._type}](id={0.id}, status={0.status}, iban={iban}, balance={balance}, {0.public_uuid})>".format(
            self, iban=iban, balance=self.balance["value"]
        )


class BunqTab(BunqObject):
    @property
    def url(self):
        # return "/".join([URL_BUNQME_API,VERSION,MERCHANT_REQUEST])
        return f"/user/{self.client.id}/monetary-account/{self.client.basic_auth.current_monetary_account.id}/bunqme-tab/"

    async def update(self):
        self.__dict__.update(
            (await self.client.request("GET", self.url + str(self.id)))[0][self._type]
        )


class BunqMeMerchantRequest(BunqObject):
    @property
    def url(self):
        from ._bunqme import URL_BUNQME_API, VERSION, MERCHANT_REQUEST

        return "/".join([URL_BUNQME_API, VERSION, MERCHANT_REQUEST])

    async def update(self):
        with self.client.foreign_base_url(self.url):
            self.__dict__.update(
                (await self.client.request("GET", self.uuid))[0][self._type]
            )
            # return self.__class__( * await self.client.request("GET", self.uuid))
