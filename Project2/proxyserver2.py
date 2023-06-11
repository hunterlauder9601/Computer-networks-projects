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

# cache directory and time limit
cache_directory = "cache"
cache_timeLimit = 5

# create a new cache directory if it doesn't already exist
if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)


# handles incoming proxy requests
def handle_proxy_request(dataSocket, serverPort=28000):
    #recv bytes and decode into string
    message = dataSocket.recv(2048).decode()
    # Parse the HTTP request to get the requested file name
    filename = message.split()[1]
    # create file path for cache file
    cache_path = os.path.join(cache_directory, filename.replace('/', '_'))

    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) <= cache_timeLimit:
        # given that the cache file exists and is valid (no timeout yet), read from the cache file
        f = None
        try:
            f = open(cache_path, 'rb')
            response = b""
            while True:
                data = f.read(2048)
                if not data:
                    break
                response += data

            print("Cache hit for {}".format(filename))
            print("proxy-cache,client,{},{}".format(threading.current_thread().ident, int(time.time())))
        finally:
            if f:
                f.close()

    else:
        # given that the cache file doesn't exist or timeout occured, forward the request to the server
        proxyToWebSocket = socket(AF_INET, SOCK_STREAM)
        proxyToWebSocket.connect(('149.125.188.111', serverPort))
        proxyToWebSocket.sendall(message.encode())
        print("proxy-forward,server,{},{}".format(threading.current_thread().ident, int(time.time())))

        # receives response from the server
        response = b""
        while True:
            data = proxyToWebSocket.recv(2048)
            if not data:
                break
            response += data


        #saves it to the cache file
        f = None
        try:
            f = open(cache_path, 'wb')
            f.write(response)
        finally:
            if f:
                f.close()

        print("Cache updated for {}".format(filename))

        proxyToWebSocket.close()

    # sends the response to the client (regardless to whether there was a cache hit or not)
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
