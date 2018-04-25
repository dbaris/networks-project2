import socket
import threading
import signal
import sys
import ssl
import re
import subprocess


from cache import LFU_Cache

resolv = {}

class Request :
    def __init__(self, data) :
        global resolv

        first_line = data.split('\n')[0]                   

        self.key_word = first_line.split(' ') [0]                    
        self.url = first_line.split(' ') [1]                    

        http_pos = self.url.find("://")          
        if (http_pos==-1):
            temp = self.url
        else:
            temp = self.url[(http_pos+3):]       
        
        port_pos = temp.find(":")           

        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        self.host = ""
        self.port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      
            self.port = 80
            self.host = temp[:webserver_pos]
        else:                                               
            self.port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            self.host = temp[:port_pos]

        self.addr = None
        if (self.host in resolv.keys()):
            addr = resolv[self.host]
        else:
            tmp = subprocess.check_output(["nslookup", self.host])
            tmp = tmp.decode()
            results = tmp.split("\n")
            for result in results:
                match = re.match("^address:\t([^ ]+).*$", result.strip(), re.I)
                if (match):
                    self.addr = match.group(1).split("#")[0]
            resolv[self.host] = self.addr
        


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
        
        request = Request(r.decode())

        try : 
            if (request.key_word == "GET") :
                # create a socket to connect to the web server
                server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_conn.settimeout(config['TIMEOUT'])
                server_conn.connect((request.host, request.port))
                server_conn.sendall(r)                           

                while (1) :
                    data = server_conn.recv(config['MAX_LEN'])         # receive data from web server
                    if (len(data) > 0):
                        client_conn.send(data)                      # send to browser
                    else:
                        break
       
            elif (request.key_word == "CONNECT") : 
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
                context.check_hostname = False

                server_conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=request.addr)
                server_conn.settimeout(config['TIMEOUT'])
                # server_conn.connect((request.host, 443))
                server_conn.connect((request.host, request.port))
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




