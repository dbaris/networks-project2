import socket
import threading
import signal
import sys

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
            process = threading.Thread(name=self._getClientName(cli_addr), target=self.start_thread, args=(cli_sock, cli_addr))
            process.setDaemon(True)
            process.start()
            print("hiiii")
        self.shutdown(0,0)
        print("leaving")

    def parse_request (request) :
        first_line = request.split('\n')[0]
        print("first line: ", first_line)
        url = first_line.split(' ')[1]
        print("url: ", url)

        http_pos = url.find("://")
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]

        port_pos = temp.find(":") 

        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:                                               # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        print("webserver: ", webserver)
        print("port: ", port)

        return webserver, port, url

    def start_thread(self, conn, client_addr) : 
        request = conn.recv(config['MAX_LEN'])
        print("request: ", request)
        webserver, port, url = parse_request(request)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(config['TIMEOUT'])
            s.connect((webserver, port))
            s.sendall(request)                           

            while 1:
                data = s.recv(config['MAX_LEN'])          # receive data from web server
                if (len(data) > 0):
                    conn.send(data)                               # send to browser
                else:
                    break
            s.close()
            conn.close()
        except socket.error as error_msg:
            print ("ERROR: ", client_addr, error_msg)
            if s:
                s.close()
            if conn:
                conn.close()

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




