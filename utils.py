import hashlib
import select


TIMEOUT_MILLIS = 1000
MAX_MSG_SIZE = 2048
SENDER = 'sender_sidkr'
RECEIVER = 'receiver_sidrk'


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



def checksum(msg):
   return hashlib.sha256(msg).hexdigest()
def blastpackets(message, addr, sock):
    i = 0 
    while i <= 100:
        sock.sendto(message, addr)
        i+= 1


if __name__ == '__main__':
    print(to_bytearray(1001))
