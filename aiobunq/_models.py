def _undunder_dict(d):
    return {k: v for (k, v) in d.items() if not k[0] == "_"}


class BunqObject(object):
    # todo: ugly, tidy it up
    def __init__(self, o: dict):
        self._type, data = o.copy().popitem()
        self.__dict__.update(data)

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


class BunqMeMerchantRequest(BunqObject):


    @property
    def url(self):
        from ._bunqme import URL_BUNQME_API, VERSION, MERCHANT_REQUEST
        return "/".join([URL_BUNQME_API,VERSION,MERCHANT_REQUEST])

    def update(self):
        pass



