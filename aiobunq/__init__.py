"""

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


def createClient(api_key=None):
    """Creates a Client, nog logged in yet.

    Args:
        api_key:
            BUNQ Api Key, if not provided, the client is automatically being switched to sandbox

    Returns: Client

    """

    from ._auth import BasicAuth

    return Client(BasicAuth(api_key))


def restore(file=None):
    """Restores the current client, session and keys from disk (if save option is used on client)
    Args:
        file: optional filepath string. if left empty the default location is ```Client.DEFAULT_STORE_FP```

    Returns:

    """
    return Client.restore(file)
