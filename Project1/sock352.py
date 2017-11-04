
import binascii
import socket as syssock
import threading
import struct
import sys
import random
import copy


# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from
udp_sock = 0
sender_port = 0
reciver_port = 0
header_pack_format = '!BBBBHHLLQQLL'
# this will be used more for next project I think, counts active sockets
num_active_sockets = 0
thread_event = threading.Event();

# Complex buffer holder for every socket
# first is dict of addresses to another dict of ports to tuple of header and data
buffers = {}

SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0xA0

SOCK352_VER      = 1
SOCK352_BUF_SIZE = 4096
SOCK352_HDR_SIZE = 40



def init(UDPportTx,UDPportRx):   # initialize your UDP socket here 
    print("doing init")

    global udp_sock
    global sender_port
    global reciver_port

    udp_sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

    reciver_port = UDPportRx
    udp_sock.bind(('', reciver_port))
    # udp_sock.settimeout(0.2)

    if UDPportTx != '':
        sender_port = UDPportTx
    else:
        sender_port = UDPportRx

    pass
    
class socket:
    
    def __init__(self):  # fill in your code here 
        print("initializing a socket")
        # init packet header parameters
        self.version = 1
        self.sequence_no = 0
        self.ack_no = 0
        self.waiting_for_ack = 0
        self.connected_address = ()

        return
    
    def bind(self,address):
        return 

    def connect(self,address):  # fill in your code here 
        print("starting connection function")
        global udp_sock
        global sender_port
        self.sequence_no = random.randint(1, 129)
        self.ack_no = 0

        packet = (SOCK352_VER, # version
                  SOCK352_SYN, # flags
                  SOCK352_HDR_SIZE,
                  self.sequence_no,
                  self.ack_no,
                  1) # payload size

        packet_string = make_packet(packet, '')

        smart_send(packet_string, address)
       
        # timeout thread is unneccesary but will be good for next proj

        threading.Thread(name = 'timeout',
                     target = self.do_timeout,
                     args = (packet_string, address))
        while(True):
            ack_header, data, back_address = get_packet(SOCK352_HDR_SIZE)

            if(back_address[1] != sender_port):
                continue

            if(validate_header(ack_header, SOCK352_SYN | SOCK352_ACK, 1)):
                self.waiting_for_ack = 0
                break
            elif(validate_header(ack_header, SOCK352_RESET, 1)):
                self.waiting_for_ack = 0
                break

        # still need last ack 
        # self.ack_no += 1
        packet = (SOCK352_VER,
                  SOCK352_ACK,
                  SOCK352_HDR_SIZE,
                  self.sequence_no,
                  self.ack_no,
                  1)

        packet_string = make_packet(packet_string, '')

        smart_send(packet_string, address)
        self.connected_address = address
        return 
    
    def listen(self,backlog):

        return

    def accept(self): 
        print("starting accept function")
        global udp_sock

        self.ack_no = 0
        self.sequence_no = 0

        while(True):
            syn_header, data, address = get_packet(SOCK352_HDR_SIZE)

            if(back_address[1] != sender_port):
                continue

            if(validate_header(ack_header, SOCK352_SYN, 0)):
                break
        
        
        self.sequence_no = random.randint(1, 129)

        packet = (SOCK352_VER, # version
                  SOCK352_SYN | SOCK352_ACK, # flags
                  SOCK352_HDR_SIZE,
                  seq_num,
                  self.ack_no,
                  1) # payload size

        packet_string = make_packet(packet, '')
        smart_send(packet_string, address)

        # try deep copy
        clientsocket = copy.deepcopy(self)
        clientsocket.connected_address = address
        self.ack_no = 0
        self.connected_address = 0


        return (clientsocket,address)
    
    def close(self):   # fill in your code here 
        return 

    def send(self,buffer):
        bytessent = 0     # fill in your code here 
        return bytesent 

    def recv(self,nbytes):
        bytesreceived = 0     # fill in your code here
        return bytesreceived 
    # Gets the next packet
    # future version will have a buffer to add packets that aren't the ones you are looking for
    def get_packet(self, packet_data_size):       
        print("starting get_packet function")
        global udp_sock
        get_packer = struct.Struct(header_pack_format)
        header = ''
        packet = ''

        while(packet_data_size > 0):
            tmp, address = udp_sock.recvfrom(packet_data_size)
            packet_data_size -= len(tmp)
            packet = ''.join(packet, tmp)

        header, data = packet[0:40], packet[40:]

        
        return get_packer.unpack(header), data, address

    # first arg is tuple with packet info, second is data
    def make_packet(self, header, data):
        print("starting make_packet function")
        packer = struct.Struct(header_pack_format)
        # self.sequence_no = header[3]
        # self.ack_no = header[4]
        return packer.pack(header[0], header[1], 0, 0, header[2], 0, 0, 0, header[3], header[4], 0, header[5]) + data
        

    def validate_header(self, header, ack, expected_add):
        print("starting validate_header function")
        global sender_port

        if( (header[0] != SOCK352_VER) or
            ( (header[1] != ack) ) or
            (header[4] != SOCK352_HDR_SIZE) or
            ( (expected_add + self.sequence_no) != header[9] )):
            return False

        # their sequence number plus the amount of data you got
        self.ack_no = header[8] + header[11]
       
        self.sequence_no = header[9]
        return True

    
    def do_timeout(self, data, address):
        print("starting do_timeout function")
        while(self.waiting_for_ack):
            time.sleep(0.2)
            smart_send(data, address)

        return

    def smart_send(self,data, address):
        print("starting smart_send function")
        global udp_sock
        size = len(data)
        tmp = 0

        while(tmp != size):
          tmp += udp_sock.sendto(data[tmp:], address)

        self.waiting_for_ack = 1
        return