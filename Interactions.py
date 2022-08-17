import sys
import pickle
import struct
import threading
import socket
import socketserver

SERVER = {
    'ip': '10.0.0.1',
    'port': 10000,
}
GATEWAYS = {
    '0':{
        'ip': '10.0.0.2',
        'port': 50001,
    }
    '1':{
        'ip': '10.0.0.3',
        'port': 50002,
    }
    '2':{
        'ip': '10.0.0.4',
        'port': 50003,
    }
    '3':{
        'ip': '10.0.0.5',
        'port': 50004,
    }
    '4':{
        'ip': '10.0.0.6',
        'port': 50005,
    }
    '5':{
        'ip': '10.0.0.7',
        'port': 50006,
    }
    '6':{
        'ip': '10.0.0.8',
        'port': 50007,
    }
    '7':{
        'ip': '10.0.0.9',
        'port': 50008,
    }
}
ITERATION_FLAG = {
    0: 'MSG_INIT',
    1: 'MSG_GLO_SYNC',
    2: 'MSG_LOAD_FINISHED',
    3: 'MSG_TRAIN_FINISHED',
    4: 'MSG_NEW_TERM',
}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
 
    def setup(self):
        self.request.sendall("Connection established!")
        g_conn_pool.append(self.request)
 
    def handle(self):
        global g_local_param_list, g_conn_pool
        while True:
            try:
                msg = recv_msg(self.request)
                if not msg: 
                    self.remove()
                    break
                if msg[0] == ITERATION_FLAG['3']:
                    lock1.acquire()
                    g_local_param_list.append(msg)
                    lock1.release()
                if msg[0] == ITERATION_FLAG['2']:
                    lock2.acquire()
                    g_load_finished_signal.append(msg)
                    lock2.release()
            except:
                self.remove()
                break
 
    def finish(self):
        self.request.close()
 
    def remove(self):
        g_conn_pool.remove(self.request)
 
class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def send_msg(sock, msg):
    msg_pickle = pickle.dumps(msg)
    sock.sendall(struct.pack(">I", len(msg_pickle)))
    sock.sendall(msg_pickle)
    print(msg[0], 'sent to', sock.getpeername())

def recv_msg(sock):
    msg_len = struct.unpack(">I", sock.recv(4))[0]
    msg = sock.recv(msg_len, socket.MSG_WAITALL)
    msg = pickle.loads(msg)
    print(msg[0], 'received from', sock.getpeername())
    return msg

if __name__=="__main__":
    '''Connect'''
    # For centric server
    ADDRESS = (SERVER['ip'], SERVER['port'])
    global g_conn_pool
    g_conn_pool = []
    
    lock = threading.RLock()
    global g_local_param_list  # store local param update
    g_local_param_list = []
    
    lock2 = threading.RLock()
    global g_load_finished_signal
    g_load_finished_signal = []
    
    tcp_server = ThreadingTCPServer(ADDRESS, ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=tcp_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # # For gateways
    # s = socket.socket()
    # s.connect((SERVER['ip'], SERVER['port']))
