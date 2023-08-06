import logging
import xmlrpc.client


def connect_daemon(host: str, port: str):
    return xmlrpc.client.ServerProxy(
        "http://{host}:{port}".format(host=host, port=port)
    )


def get_client(host: str, port: str):
    try:
        s = connect_daemon(host, port)
        if s.isAlive() is not True:
            return None
        return s
    except ConnectionRefusedError as err:
        logging.debug(f"Connection refused {err}")
        return None
    except Exception as err:
        logging.debug("we got exception here")
        print(f"Unexpected {err=}, {type(err)=}")
        return None
