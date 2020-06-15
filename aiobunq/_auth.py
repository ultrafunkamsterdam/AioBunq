# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# part of aiobunq package
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import pickle


__all__ = ["BasicAuth"]


class BasicAuth:
    """ User authentication data object which holds user/session info in scalar data
        and is able to save/restore to disk.

        Args:
            api_key: bunq production api key. if not supplied, sandbox mode is activated.
    """

    def __init__(self, api_key=None):

        self._api_key = api_key
        self._sandbox = not api_key
        self._token = None
        self._session_token = None
        self._private_key = None
        self._public_key = None
        self._public_key_peer = None
        self._device_id = None
        self._last_auth_timestamp = None
        self._user = None
        self._monetary_accounts = None
        self._current_monetary_account = None

    @property
    def id(self):
        return self._user["id"]

    @property
    def status(self):
        if self.is_session_established:
            return "session"
        else:
            return "new"

    @property
    def is_installed(self):
        return bool(self.token)

    @property
    def is_device_registered(self):
        return bool(self.device_id)

    @property
    def is_session_established(self):
        return bool(self._session_token)

    @property
    def session_token(self):
        return self._session_token

    @session_token.setter
    def session_token(self, value):
        self._session_token = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value: str):
        self._device_id = value

    @property
    def sandbox(self):
        if not self._api_key:
            return True
        elif self._api_key.startswith("sandbox"):
            return True
        return False

    @sandbox.setter
    def sandbox(self, val):
        self._sandbox = val

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, key: str):
        self._api_key = key

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, key: str):
        self._private_key = key

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, key: str):
        self._public_key = key

    @property
    def public_key_peer(self):
        return self._public_key_peer

    @public_key_peer.setter
    def public_key_peer(self, key: str):
        self._public_key_peer = key

    @property
    def monetary_accounts(self):
        return self._monetary_accounts

    @monetary_accounts.setter
    def monetary_accounts(self, value):
        self._monetary_accounts = value

    @property
    def current_monetary_account(self):
        return self._current_monetary_account

    @current_monetary_account.setter
    def current_monetary_account(self, value):
        self._current_monetary_account = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @classmethod
    def load_file(cls, filename):
        with open(filename, "r+b") as f:
            state = pickle.load(f)
        instance = cls()
        instance.__dict__.update(state)
        return instance

    def save_file(self, filename):
        with open(filename, "w+b") as f:
            pickle.dump(self.__dict__, f)

    def __repr__(self):
        return f"<[{self.__class__.__name__}]({self.status})>"


class Auth:
    """Main authorization protocol

    args:
        basic_auth: BasicAuth object
                    if not provided, it will be used by sandbox
    """

    RSA_BITS = 2048

    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Signature import PKCS1_v1_5

    def __init__(self, basic_auth: BasicAuth = None):
        """Creates the security protocol around a simple basic auth object

        :param BasicAuth basic_auth: an instance of BasicAuth
        """
        self.__auth = basic_auth
        self._priv = None
        self._pub = None
        self._peer_pub = None

        if basic_auth.sandbox or not basic_auth.is_installed:
            key = self.RSA.generate(self.RSA_BITS)
            basic_auth.private_key = key.export_key("PEM").decode()
            basic_auth.public_key = key.publickey().export_key("PEM").decode()
        self.private_key = basic_auth.private_key
        self.peer_public_key = basic_auth.public_key_peer

    @property
    def peer_public_key(self):
        return self._peer_pub

    @peer_public_key.setter
    def peer_public_key(self, key: str):
        if key is not None:
            self._peer_pub = self.RSA.import_key(key)

    @property
    def public_key(self):
        return self._priv.publickey()

    @property
    def private_key(self):
        return self._priv

    @private_key.setter
    def private_key(self, key: str):
        if key is not None:
            self._priv = self.RSA.import_key(key)

    def sign(self, payload: bytes):
        digest = self.SHA256.new(payload)
        return self.PKCS1_v1_5.new(self.private_key).sign(digest)

    def verify(self, payload: bytes, signature: bytes):
        digest = self.SHA256.new(payload)
        return self.PKCS1_v1_5.new(self.peer_public_key).verify(digest, signature)
