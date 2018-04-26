import socket
import threading
import signal
import sys
import contentfilter
import cache
from http.server import BaseHTTPRequestHandler
import io


class Request (BaseHTTPRequestHandler):
    def __init__(self, request) :
        self.rfile = io.BytesIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
        try:
            self.host, self.port = self.headers['host'].split(":")
        except AttributeError :
            self.host = None
            self.port = None
        except :
            self.port = None
            self.host = self.headers['host']

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
        while True:
            (cli_sock, cli_addr) = self.serverSocket.accept()
            process = threading.Thread(name=self._get_name(cli_addr), target=self._start_thread, args=(cli_sock, cli_addr))
            process.setDaemon(True)
            process.start()
        self.shutdown(0,0)

    def _start_thread(self, client_conn, client_addr):
        r = client_conn.recv(config['MAX_LEN'])       

        request = Request(r)
        if (request.host is None) : 
            client_conn.close()
            return

       
        cacheData = cache.get(request.path)
        if cacheData is not None:
            print("Found in cache!")
            client_conn.send(cacheData)
            # s.close()
            client_conn.close()
            return

        # Content filter - keywords should be automated
        filter = contentfilter.ContentFilter()
        filter.addKeyword("Indigenous")
        filter.addKeyword("Women")
        filter.addKeyword("sexual misconduct")
        filter.addKeyword("assault")

        try : 
            if (request.command == "GET") :
                if (request.port is None) :
                    request.port = 80

                server_conn = self._create_sock(request)
                server_conn.sendall(r)                           

                while 1:
                    data = server_conn.recv(config['MAX_LEN'])         # receive data from web server
                    if (len(data) > 0):
                        # print("data : ", data.decode())
                        try:
                            data_filtered = filter.filterPage(data.decode())
                            client_conn.send(data_filtered.encode())
                            if data_filtered != "":
                                cache.add(request.path, data_filtered.encode())
                        except UnicodeDecodeError:
                            client_conn.send(data)                      # send to browser
                    else:
                        break
       
            elif (request.command == "CONNECT") : 
                
                if (request.port is None) :
                    request.port = 443
                
                server_conn = self._create_sock(request)

                conn_resp = "HTTP/1.1 200 Connection established\r\n"+"Proxy-agent: Pyx\r\n"+"\r\n"
                client_conn.sendall(conn_resp.encode())

                print("sent established connection")
                
                data = client_conn.recv(config['MAX_LEN'])         
                server_conn.send(data)
               
                print("data sent")

                while (1) :
                    data = server_conn.recv(config['MAX_LEN'])         
                    if (len(data) > 0):
                        client_conn.send(data)
                    else:
                        break

            
            server_conn.close()
            client_conn.close()

        except socket.error as error_msg:
            print ("ERROR: ",client_addr,error_msg)
            if server_conn:
                server_conn.close()
            if client_conn:
                client_conn.close()


    def _create_sock(self, request) :
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(config['TIMEOUT'])
        conn.connect((request.host, (int)(request.port)))
        return conn

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
            "TIMEOUT" : 10 
        }
    cache = cache.LFU_Cache(100)
    proxy = Proxy(config)
    proxy.listen()