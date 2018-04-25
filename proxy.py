import socket
import threading
import signal
import sys
import ssl
import re
import subprocess
from http.server import BaseHTTPRequestHandler
import io


from cache import LFU_Cache

class Request (BaseHTTPRequestHandler):
    def __init__(self, request) :
        self.rfile = io.BytesIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

        try:
            self.port = self.headers['host'].split(":")[1]
        except:
            self.port = None
        # self.client_address
        # self.addr = self.address_string()
        


class Proxy :
    def __init__(self, config) :
        # Shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.close_connect)     

        # Create a TCP socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   

        # bind the socket to a public host, and a port 
        self.serverSocket.bind((config['HOST'], config['PORT'])) 

        # become a server socket
        self.serverSocket.listen(10)    
        
        self.__clients = {}

    def listen(self) :
        print("hello")
        while True:
            (cli_sock, cli_addr) = self.serverSocket.accept()
            print("eyo")
            process = threading.Thread(name=self._get_name(cli_addr), target=self.start_thread, args=(cli_sock, cli_addr))
            process.setDaemon(True)
            process.start()
            print("hiiii")
        self.shutdown(0,0)
        print("leaving")

    def start_thread(self, client_conn, client_addr):

        r = client_conn.recv(config['MAX_LEN'])        # get the request from browser
        
        request = Request(r)

        try : 
            if (request.command == "GET") :
                # create a socket to connect to the web server
                if (request.port is None) :
                    request.port = 80
                server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_conn.settimeout(config['TIMEOUT'])
                server_conn.connect((request.headers['host'], request.port))
                server_conn.sendall(r)                           

                while (1) :
                    data = server_conn.recv(config['MAX_LEN'])         # receive data from web server
                    if (len(data) > 0):
                        client_conn.send(data)                      # send to browser
                    else:
                        break
       
            elif (request.command == "CONNECT") : 
                if (request.port is None) :
                    request.port = 443
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
                context.check_hostname = False

                server_conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=request.address_string())
                server_conn.settimeout(config['TIMEOUT'])
                # server_conn.connect((request.host, 443))
                server_conn.connect((request.headers['host'], request.port))
                # newrequest = "GET "+url+" HTTP/1.1\r\n"+"Host: "+webserver+"\r\n"+"Connection: close\r\n"+"\r\n"
                # print("request: ", request)

                # request = request.encode()
                print("request: ", r.decode())
                server_conn.sendall(r)
                
                resp = ""
                while (1) :
                    temp = server_conn.recv(config['MAX_LEN']).decode()
                    if (not temp):
                        break
                    resp += temp
                print("resp: ", resp)
                client_conn.sendall(resp.encode())
            
            server_conn.close()
            client_conn.close()

        except socket.error as error_msg:
            print ("ERROR: ",client_addr,error_msg)
            if server_conn:
                server_conn.close()
            if client_conn:
                client_conn.close()


    # def _parse_request (request) :
    #     first_line = request.split('\n')[0]
    #     print("first line: ", first_line)
    #     url = first_line.split(' ')[1]
    #     print("url: ", url)

    #     http_pos = url.find("://")
    #     if (http_pos==-1):
    #         temp = url
    #     else:
    #         temp = url[(http_pos+3):]

    #     port_pos = temp.find(":") 

    #     webserver_pos = temp.find("/")
    #     if webserver_pos == -1:
    #         webserver_pos = len(temp)

    #     webserver = ""
    #     port = -1
    #     if (port_pos==-1 or webserver_pos < port_pos):      # default port
    #         port = 80
    #         webserver = temp[:webserver_pos]
    #     else:                                               # specific port
    #         port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
    #         webserver = temp[:port_pos]

    #     print("webserver: ", webserver)
    #     print("port: ", port)

    #     return webserver, port, url

    # def start_thread(self, conn, client_addr) : 
    #     request = conn.recv(config['MAX_LEN'])
    #     print("request: ", request)
    #     webserver, port, url = _parse_request(request)

    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         s.settimeout(config['TIMEOUT'])
    #         s.connect((webserver, port))
    #         s.sendall(request)                           

    #         while 1:
    #             data = s.recv(config['MAX_LEN'])          # receive data from web server
    #             if (len(data) > 0):
    #                 conn.send(data)                               # send to browser
    #             else:
    #                 break
    #         s.close()
    #         conn.close()
    #     except socket.error as error_msg:
    #         print ("ERROR: ", client_addr, error_msg)
    #         if s:
    #             s.close()
    #         if conn:
    #             conn.close()

    def _get_name(self, cli_addr):
        return "Client"

    def close_connect(self):
        self.serverSocket.close()
        sys.exit(0)



if __name__ == "__main__":
    if len(sys.argv) != 2 :
        print("usage: ", sys.argv[0], "<port>");
        sys.exit(1);

    config =  {
            "HOST" : "0.0.0.0",
            "PORT" : int(sys.argv[1]),
            "MAX_LEN" : 1024,
            "TIMEOUT" : 5 
        }

    proxy = Proxy(config)
    proxy.listen()


# https://github.com/dpallot/simple-websocket-server/blob/master/SimpleWebSocketServer/SimpleWebSocketServer.py#L26



