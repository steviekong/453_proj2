import socket
import argparse
import select
from timeit import default_timer as timer
import utils
import os 


class ChatClientReceiver:
    def __init__(self, sock, address):
        self.sock = sock
        self.address = address  # we will send/recive data from this address
        self.fout = None  # file to write
        self.first_datagram = True
        self.data_size = None
    
    def recv_output_filename(self, data):
        if data.startswith('FILENAME'):
            parts = data.split(' ')
            if len(parts) == 3:
                output_file = parts[1]
                size = parts[2]
            if output_file != None:
                self.fout = open(output_file, 'wb')
                self.data_size = int(size)
                print('got the file name: '+ output_file +' size ' + size)
            self.first_datagram = False
            return True
        return False
    
    def rdt_recv(self):
        expecting_sequence = 0
        is_first = True
        all_data = b''
        start = timer()
        while True:
            end = timer()
            print(end-start)
            if int(end-start)  >= 300:
                print("TIMER EXPIRED")
                break;
            if self.data_size != None and int(self.data_size) <= 0:

                break

            message, self.address = self.sock.recvfrom(2048)
            checksum = message[:64]
            seq = message[64:65]
            content = message[65:]
            try :
                if utils.checksum(content) == checksum.decode():

                    checksum = utils.checksum(content)
                    ##print('checksum passed sending ACK ' +(str(utils.checksum("ACK" +str(seq.decode())))+"ACK" +str(seq.decode())))
                    print('checksum passed sending ack ' + utils.checksum("ACK".encode()+seq)+ "ACK"+seq.decode())
                    self.sock.sendto(utils.checksum("ACK".encode()+seq).encode()+"ACK".encode()+seq, self.address)
            
                    print("expecting_sequence " + str(expecting_sequence))
                    if int(seq) == expecting_sequence:
                        if is_first:
                            print('first_datagram')
                            self.recv_output_filename(content.decode()) 
                            is_first = False
                        else:
                            self.data_size = self.data_size -  len(content)
                            print('content recieved writing to file data left is '+  str(self.data_size))
                            all_data += content
                        expecting_sequence = 1 - expecting_sequence
                else:
                    print("checksum failed sending NAk "+ utils.checksum(content))
                    #self.sock.sendto((str(utils.checksum("ACK" +str(1 - expecting_sequence)))+"ACK" +str(1 - expecting_sequence)).encode(), self.address)
                    self.sock.sendto(utils.checksum("ACK".encode()+ str((1-expecting_sequence)).encode()).encode()+"ACK".encode()+str((1-expecting_sequence)).encode(), self.address)
            except: 
                print("checksum failed sending NAk "+ utils.checksum(content))
                #self.sock.sendto((str(utils.checksum("ACK" +str(1 - expecting_sequence)))+"ACK" +str(1 - expecting_sequence)).encode(), self.address)
                self.sock.sendto(utils.checksum("ACK".encode()+ str((1-expecting_sequence)).encode()).encode()+"ACK".encode()+str((1-expecting_sequence)).encode(), self.address)

        print('writing data')
        self.fout.write(all_data)
        self.fout.flush()
        os.fsync(self.fout)
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
        receiver.rdt_recv()
    finally:
        # FIXME: close connection so receiver gracefully exits
        sock.sendto(b'.', serv_addr)
        sock.sendto(b'QUIT', serv_addr)