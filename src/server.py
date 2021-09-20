# Communication Platform - Server

import socket
import threading

DEFAULT_HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
DEFAULT_PORT = 65430        # Port to listen on (non-privileged ports are > 1023)

# Object Created by developers to start a server that listen for clients to connect
class CommunicationServer:  # External
  Clients = []
  MaxConcurrentClients = 8
  _main_thread = None
  _debug = False
  _interrupt = False

  #Maybe we cou
  def Host(self, port=DEFAULT_PORT):
      self._mainThread = threading.Thread(target=self.serve, args=[port])
      self._mainThread.start()
      print("Max Concurrent: ", self._maxConcurrent)

  def serve(self, port=DEFAULT_PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.bind((DEFAULT_HOST, DEFAULT_PORT))
      s.settimeout(5)
      #s.listen()

      if self.debug:
        print('Listening on port: ' + str(port))

      while True:
        s.listen()
        try:
          conn, addr = s.accept()
          if len(self._clients) >= self._maxConcurrent:
            if self.debug:
                print(' *** Connection Refused: Max Concurrent Clients Reached (',
                      len(self._clients), '/', self._maxConcurrent, ')')

            conn.sendall(b'MaxClientsReached')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
          else:
            conn.settimeout(10)
            thread = threading.Thread(
                target=self.accept, args=[conn, addr])
            thread.start()
        except:
          if self._interrupt:
            if self.debug:
                print('Port ' + str(port) + ': Shutting Down')
            return

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
                    #TODO Make sure we can recieve more than 1024B
                    data = conn.recv(1024)
                    # If Recieved Data is empty, assume connection has been lost and raise Exception
                    conn.sendall(data)
                    # If Recieved data is 'q', call shutdown socket on server
                    if (data.decode() == 'q'):
                        #conn.shutdown(socket.SHUT_RDWR)
                        #conn.close()
                        self.close(conn,addr,threading.current_thread(),id)
                        if self.debug:
                            print('Closing connection on port: ' + str(DEFAULT_PORT))
                        break
                # Handle Connection Lost
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



  def __init__(self, debug=False):
    self._debug = debug


class ClientConnectionInfo:
  port = 1


class Client:
  Socket = None
  PlayerInfo = None


class PlayerInfo:
  GamesPlayed = 0
  GamesLeft = 0
  NumberOfWins = 0
  # Send the PlayerInfo to the player via the Socket

  def SendStatistics():
    pass
