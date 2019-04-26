import socket
import select
import argparse
from timeit import default_timer as timer

import utils


class ChatClientSender:
    def __init__(self, sock, address, rdr, remote_op_file):
        self.sock = sock
        self.address = address  # we will send/recive data from this address
        self.rdr = rdr  # read data from reader
        self.remote_op_file = remote_op_file  # file to which the receiver should write
    
    def send_byte_stream(self):
        '''
            Reads from the input stream and sends the read bytes reliably and
            in-order by invoking rdtSend.
        '''

        while True:
            data = self.rdr.read()
            if data:
                self.rdt_send('FILENAME ' + self.remote_op_file, data, 1983)
            else:
                break
    
    def rdt_send(self, filename, data, segment_size):

        offset = 0
        seq = 0
        is_first = False
        start = timer()
        while offset < len(data):
            end = timer()
            print(end-start)
            if int(end-start)  >= 200:
                print("TIMER EXPIRED")
                break;
            if is_first == True:
                if offset + segment_size > len(data):
                    segment = data[offset:]
                else:
                    segment = data[offset:offset+segment_size]
                offset += segment_size
            ack = False 
            while not ack:
                end = timer()
                print(end-start)
                if int(end-start)  >= 200:
                    print("TIMER EXPIRED")
                    break;
                if is_first == False:
                    tosend = (filename+ ' ' + str(len(data))).encode()
                    #self.sock.sendto((str(utils.checksum(filename+ ' ' +str(len(data))))+str(seq)+filename+' '+str(len(data))).encode(), self.address)
                    self.sock.sendto(utils.checksum(tosend).encode()+str(seq).encode()+tosend, self.address)
                    print("sending filename " + (utils.checksum(tosend).encode()+tosend).decode())
                else:
                    print("sending DATA")
                    self.sock.sendto(utils.checksum(segment).encode()+str(seq).encode()+segment, self.address)
                    print('checksum :'  + utils.checksum(segment) + 'seq: '+ str(seq) )
                try:
                    message, self.address = self.sock.recvfrom(2048)
                except socket.timeout:
                    print('timeout')
                else:
                    try: 
                        print(message)
                        checksum = message[:64]
                        print('checksunm is '+ checksum.decode())
                        ack_seq = message[67:68] 
                        print('ack is '+ str(ack_seq))  
                        if utils.checksum(message[64:]) == checksum.decode() and ack_seq.decode() == str(seq):
                            print('got valid ack ' + ack_seq.decode())
                            ack = True 
                            is_first = True
                    except:
                        pass
                  
            seq = 1 - seq
    
    def send_remote_output_filename(self):
        print('sending the file called ' + self.remote_op_file)
        rdt_send(b'FILENAME ' + self.remote_op_file.encode(), 2048)
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Receiver')
    parser.add_argument('-s', dest='server_ip', required=True,
                        help='server ip address')
    parser.add_argument('-p', dest='server_port', required=True,
                        help='server port')
    parser.add_argument('-t', dest='files', required=True, nargs=2,
                        help='server port')

    args = parser.parse_args()
    serv_addr = (args.server_ip, int(args.server_port))
    input_file, output_file = args.files[0], args.files[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)

    try:
        # send NAME message
        intro = utils.introduce_myself(sock, serv_addr, utils.SENDER.encode())
        while not intro:
            pass
        # send CONN message
        setup = utils.setup_connection(sock, serv_addr, utils.RECEIVER.encode())
        while not setup:
            pass
        if intro == True and setup == True:
            print('setup and intro done')
            with open(input_file, mode='rb') as rdr:
                sender = ChatClientSender(sock, serv_addr, rdr, output_file)
                # send FILENAME
                sender.send_byte_stream()
    finally:
        # FIXME: close connection so receiver gracefully exits
        print('closing')
        sock.sendto(b'.', serv_addr)
        sock.sendto(b'QUIT', serv_addr)