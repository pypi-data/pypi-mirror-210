import socket


def multicastIP():
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007
    MULTICAST_TTL = 2

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

    message = "{}".format(get_ip())
    encoded = message.encode('utf-8')  # encode to get bytelike object
    s.sendto(encoded, (MCAST_GRP, MCAST_PORT))
    return None


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


def receiveIP(portNr):
    s = socket.socket(socket.AF_INET,  # Internet
                      socket.SOCK_DGRAM)  # UDP
    s.bind(('', 1234))
    while True:
        data, addr = s.recvfrom(4096)  # buffer size is 1024 bytes
        print("received message:", data.decode('utf-8'))
