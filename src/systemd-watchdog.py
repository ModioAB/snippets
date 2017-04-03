import os
import socket


def watchdog_socket(clean_environment=True):
    """clean_environment removes the varaibles from env to prevent children
    from inheriting it and doing something wrong"""

    _empty = None, None
    address = os.environ.get("NOTIFY_SOCKET", None)
    if clean_environment:
        address = os.environ.pop("NOTIFY_SOCKET", None)

    if not address:
        return _empty

    if len(address) == 1:
        return _empty

    if address[0] not in ("@", "/"):
        return _empty

    if address[0] == "@":
        address = "\0" + address[1:]

    # SOCK_CLOEXEC was added in Python 3.2 and requires Linux >= 2.6.27.
    # It means "close this socket after fork/exec()
    try:
        sock = socket.socket(socket.AF_UNIX,
                             socket.SOCK_DGRAM | socket.SOCK_CLOEXEC)
    except AttributeError:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    return address, sock


def watchdog_ping(address, sock):
    message = b"WATCHDOG=1"
    if not (address and sock):
        return False
    try:
        retval = sock.sendto(message, address)
    except socket.error:
        return False

    return (retval > 0)


if __name__ == "__main__":
    import time
    watchdog = watchdog_socket()
    while True:
        watchdog_ping(*watchdog)
        time.sleep(20)
