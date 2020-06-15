"""Asyncio Interface to the BUNQ (bank) Api.

  Typical usage example:

  ```
  from aiobunq import createClient
  client = createClient(API_KEY)  # if API_KEY is None a sandbox-session is created instead
  await client.logon()

  client.save()
  ```
  ---------------------
  ```
  from aiobunq import Client
  client = Client.restore()
  await client.get_monetary_accounts()
  ```

 █████╗ ██╗ ██████╗     ██████╗ ██╗   ██╗███╗   ██╗ ██████╗
██╔══██╗██║██╔═══██╗    ██╔══██╗██║   ██║████╗  ██║██╔═══██╗
███████║██║██║   ██║    ██████╔╝██║   ██║██╔██╗ ██║██║   ██║
██╔══██║██║██║   ██║    ██╔══██╗██║   ██║██║╚██╗██║██║▄▄ ██║
██║  ██║██║╚██████╔╝    ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
╚═╝  ╚═╝╚═╝ ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚══▀▀═╝

 █████╗ ██████╗ ██╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██║    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝
███████║██████╔╝██║    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║
██╔══██║██╔═══╝ ██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║
██║  ██║██║     ██║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║
╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝


ASYNC BUNQ API CLIENT FOR PYTHON 3+


"""

from ._client import Client


__client__ = None


def createClient(api_key=None):
    """Creates a Client, nog logged in yet.

    Args:
        api_key:
            BUNQ Api Key, if not provided, the client is automatically being switched to sandbox

    Returns: Client

    """
    global __client__
    from ._auth import BasicAuth

    __client__ = Client(BasicAuth(api_key))
    return __client__


def restoreClient(filepath=None):
    """Restores the client session and keys from disk <file> (or default path when no filepath supplied)
        you can call also call the more convenient .restore() method on the Client class directly.

    Args:
        filepath: optional filepath string. if left empty the default location is ```Client.DEFAULT_STORE_FP```

    Returns: Client

    """
    global __client__
    __client__ = Client.restore(filepath)
    return __client__


def saveClient(client=None, filepath=None):
    """Helper function to saves the supplied  client, session and keys to disk <file> (or default path when no filename is supplied)
        you can call also call the more convenient .save() method on the client instance directly.

       Args:
           filepath: optional filepath string. if left empty the default location is ```Client.DEFAULT_STORE_FP```

       Returns:

       """
    global __client__
    if not client and not __client__:
        raise KeyError('You should pass the client to save.')
    elif client:
        client.save(filepath)
    elif __client__ and isinstance(__client__, Client):
        __client__.save()
