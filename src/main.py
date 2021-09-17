from os import device_encoding
import socket
import threading
import time
import random
response = input('1: Server\n2: Client\n')

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65430        # Port to listen on (non-privileged ports are > 1023)

class ConLostException(Exception):
    def __init__(self, message="Connection Lost: "):
        super().__init__(message)

class client:
    isConnected = False
    def connect(self):
        pass

class Server:

    _maxConcurrent = 8
    _interrupt = False
    #_threads = []
    #_connections = []
    _clients = {}
    _mainThread = None
    _debug = False
    _lock = threading.Lock()

    def host(self, startPort=65430, maxConcurrent=3, debug=False):
        self.debug = debug
        self._maxConcurrent = maxConcurrent
        self._mainThread = threading.Thread(target=self.serve, args=[startPort])
        self._mainThread.start()
        print("Max Concurrent: ", self._maxConcurrent)

    def serve(self, PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.settimeout(5)
            #s.listen()

            if self.debug:
                print('Listening on port: ' + str(PORT))

            while True:
                s.listen()
                try:
                    conn, addr = s.accept()
                    if len(self._clients) >= self._maxConcurrent:
                        if self.debug:
                            print(' *** Connection Refused: Max Concurrent Clients Reached (', len(self._clients) ,'/', self._maxConcurrent, ')')
                        conn.sendall(b'MaxClientsReached')
                        conn.shutdown(socket.SHUT_RDWR)
                        conn.close()
                    else:
                        conn.settimeout(10)
                        thread = threading.Thread(target=self.accept, args=[conn, addr])
                        thread.start()
                except:
                    if self._interrupt:
                        if self.debug:
                            print('Port ' + str(PORT) + ': Shutting Down')
                        return


    def terminate(self):
        graceful_shutdown = True
        self._interrupt = True

        for client in self._clients:
            self._clients[client][0].join()

            if self._clients[client][0].is_alive():
                graceful_shutdown = False

        return graceful_shutdown

    def close(self, conn, addr, thread, id):
        # Close Socket Connection
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

        #self._lock.acquire()
        self._clients.pop(id)
        #self._lock.release()

    def accept(self, conn, addr):

        if self.debug:
            print("Current thread: " + str(threading.current_thread().ident))
            print('Client Connecting...')

        conn.sendall(b'ConnectionEstablished')

        id = conn.recv(1024).decode()
        if id in self._clients:
            conn.sendall(b'IDInUse')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            return 0
        else: conn.sendall(b'ConnectionSuccess')


        self._clients[id] = (threading.current_thread(), (conn, addr))

        with conn:
            if self.debug:
                print('Connected by', addr)
            while not self._interrupt:
                try:
                    data = conn.recv(1024)
                    # If Recieved Data is empty, assume connection has been lost and raise Exception
                    if data == b'':
                        raise ConLostException()
                    conn.sendall(data)
                    # If Recieved data is 'q', call shutdown socket on server
                    if (data.decode() == 'q'):
                        #conn.shutdown(socket.SHUT_RDWR)
                        #conn.close()
                        self.close(conn,addr,threading.current_thread(),id)
                        if self.debug:
                            print('Closing connection on port: ' + str(PORT))
                        break
                # Handle Connection Lost
                except ConLostException as e:
                    print(e, addr)
                    self.close(conn,addr,threading.current_thread(),id)
                    break
                # Timeout Set to allow for exit signal to reach threads
                except socket.timeout as e: 
                        pass
                # Handle Connection Lost
                except socket.error as e:
                    print(e, addr)
                    self.close(conn,addr,threading.current_thread(),id)
                    break
                except Exception as e: 
                    if self.debug:
                        print(e, addr)
                        input('Press Any Key to Continue...')
                    else:
                        self.close(conn,addr,threading.current_thread(),id)
                        break

def sendPacket(packet, id):
    print(id)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.settimeout(10)
            connected = False
            while True:
                try:
                    if not connected:
                        connectionstatus = s.recv(1024)
                        if connectionstatus.decode() == 'MaxClientsReached':
                            print('Max Clients Reached: Connection Refused')
                            break
                        elif connectionstatus.decode() == 'ConnectionEstablished':
                            s.sendall(id.encode())
                            connectionstatus = s.recv(1024)
                            print(connectionstatus.decode())
                            if connectionstatus.decode() == 'IDInUse':
                                print('ID Already in Use: Connection Refused')
                                break
                            connected = True

                    response = input('Message: ')
                    s.sendall(response.encode())
                    data = s.recv(1024)

                    print('Received', repr(data.decode()))
                    if response == 'q':
                        s.shutdown(socket.SHUT_RDWR)
                        s.close()
                        break
                except Exception as e:
                    print(e)
                    break
        except Exception as e:
            print(e)

# Host
if response == '1':
    server = Server()
    server.host(debug=True)
    while True:
        resp = input('Console: ')
        if resp == 'q':
            print('Closing All Open Connections')
            print("Server Termination Status: " + str(server.terminate()))
            break
        elif resp == 'p':
            print(server._clients.keys())
# Client
if response == '2':
    sendPacket("Message", 'MyUserID' + str(random.randint(0,5)))


# Save State

# Load State

