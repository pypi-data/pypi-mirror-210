import socket
import struct


def get_ip():
    # get own ip Address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def listenForIP():
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007
    IS_ALL_GROUPS = True

    sockMulti = socket.socket(socket.AF_INET,
                              socket.SOCK_DGRAM,
                              socket.IPPROTO_UDP)
    sockMulti.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if IS_ALL_GROUPS:
        # on this port, receives ALL multicast groups
        sockMulti.bind(('', MCAST_PORT))
    else:
        # on this port, listen ONLY to MCAST_GRP
        sockMulti.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sockMulti.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # while True:
    #   # For Python 3, change next line to "print(sock.recv(10240))"
    #     print(sock.recv(10240))

    ip = sockMulti.recv(10240).decode('utf-8')
    sockMulti.close()
    print(ip)
    return ip


def responseIP(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    message = "{}".format(get_ip())
    sock.sendto(message.encode('utf-8'), (ip, 1234))
    return None
