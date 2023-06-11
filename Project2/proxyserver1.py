import os
import sys
import time
import threading
from socket import *

proxySocket = socket(AF_INET, SOCK_STREAM) #welcome proxy socket
proxyPort = 29000
proxySocket.bind(('', proxyPort))
proxySocket.listen(1)
#array to track threads to ensure proper closing
threads = []

# handles incoming proxy requests
def handle_proxy_request(dataSocket, serverPort=28000):
    #recv bytes and decode into string
    message = dataSocket.recv(2048)

    proxyToWebSocket = socket(AF_INET, SOCK_STREAM)
    proxyToWebSocket.connect(('149.125.188.111', serverPort))
    proxyToWebSocket.sendall(message)
    print("proxy-forward,server,{},{}".format(threading.current_thread().ident, int(time.time())))
    
    # receives response from the server
    response = b""
    while True:
        data = proxyToWebSocket.recv(2048)
        if not data:
            break
        response += data


    proxyToWebSocket.close()

    # sends the response to the client
    dataSocket.sendall(response)
    print("proxy-forward,client,{},{}".format(threading.current_thread().ident, int(time.time())))

    dataSocket.close()


try:
    while True:
        print('Proxy server is ready to serve...')
        dataSocket, addr = proxySocket.accept() #proxy data socket
        t = threading.Thread(target=handle_proxy_request, args=(dataSocket,))
        t.start()
        threads.append(t)
except KeyboardInterrupt:
    #blocks and waits for all threads to complete before shutting down
    for t in threads:
        t.join()

    proxySocket.close()
    sys.exit()
