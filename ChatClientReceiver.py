import socket
import argparse
import select

import utils


class ChatClientReceiver:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address  # we will send/recive data from this address
        self.fout = None  # file to write
        self.first_datagram = True
    
    def recv_output_filename(self, data):
        if data.startswith(b'FILENAME'):
            parts = data.split(b' ')
            if len(parts) == 2:
                output_file = parts[1]
            if output_file != None:
                self.fout = open(output_file, mode='wb')
            self.first_datagram = False
            print('got the file name')
            return True
        return False
    
    def rdt_recv(self):
        expecting_sequence = 0
        is_first = True
        size = None
        while True:
            print("Stuck")
            message, self.address = self.sock.recvfrom(2048)
            checksum = message[:2]
            seq = message[2]
            content = message[:3]

            if utils.checksum(content) == checksum:
                checksum = utils.checksum(content)
                self.sock.sendto(checksum+content, self.address)
                if seq == srt(expecting_sequence):
                    if is_first:
                        self.recv_output_filename(content)
                        is_first = False
                    else:
                        self.fout.write(content)
                    expecting_sequence -= 1
                else:
                    self.sock.sendto("ACK" +str(1 - expecting_sequence), self.address)

        self.fout.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Receiver')
    parser.add_argument('-s', dest='server_ip', required=True,
                        help='server ip address')
    parser.add_argument('-p', dest='server_port', required=True,
                        help='server port')

    args = parser.parse_args()
    serv_addr = (args.server_ip, int(args.server_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    try:
        # send NAME message
        while not utils.introduce_myself(sock, serv_addr, utils.RECEIVER.encode()):
            pass
        # send CONN message
        while not utils.setup_connection(sock, serv_addr, utils.SENDER.encode()):
            pass

        receiver = ChatClientReceiver(sock, serv_addr)
        receiver.receive_bytestream()
    finally:
		# FIXME: close connection so receiver gracefully exits
        sock.sendto(b'.', serv_addr)
        sock.sendto(b'QUIT', serv_addr)
