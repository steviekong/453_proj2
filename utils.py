import hashlib
import select


TIMEOUT_MILLIS = 1000
MAX_MSG_SIZE = 2048
SENDER = 'sender_30664666'
RECEIVER = 'receiver_30664666'


def to_bytearray(obj):
    return str(obj).encode('utf-8')


def udt_recv(sock, tries=100, timeout=0.2):
    for _ in range(tries):
        rlist, _, _ = select.select([sock], [], [], timeout)
        if sock in rlist:
            data, _ =  sock.recvfrom(MAX_MSG_SIZE)
            return data
    return b''


def introduce_myself(sock, address, name):
    # FIXME: sent packet or response may get dropped
    print('NAME ' + name.decode(), address)
    sock.sendto(b'NAME ' + name, address)

    # FIXME: check for OK response from server, else return false
    data = udt_recv(sock)
    if data.decode()[:2] == 'OK':
        return True
    else:
        print('didnt get data name')
        return False 


def setup_connection(sock, address, receiver):
    # FIXME: sent packet or response may get dropped
    print("setting up connection")
    sock.sendto(b'CONN ' + receiver, address)

    # FIXME: check for OK response from server, else return false
    data = udt_recv(sock)
    if data.decode()[:2] == 'OK':
        print(data.decode())
        return True
    else:
        print("didnt get setup")
        return False 



def checksum(data):
    s = 0
    n = len(data) % 2
    for i in range(0, len(data)-n, 2):
        s+= ord(data[i]) + (ord(data[i+1]) << 8)
    if n:
        s+= ord(data[i+1])
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xffff
    return s



if __name__ == '__main__':
    print(to_bytearray(1001))
