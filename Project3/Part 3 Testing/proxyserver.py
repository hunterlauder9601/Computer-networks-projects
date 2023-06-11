import sys
import time
import threading
from socket import *
import os

proxySocket = socket(AF_INET, SOCK_STREAM) #welcome proxy socket
proxyPort = 29000
proxySocket.bind(('', proxyPort))
proxySocket.listen(1)
#array to track threads to ensure proper closing
threads = []

# cache directory and time limit
cache_directory = "cache"
cache_timeLimit = 60

# create a new cache directory if it doesn't already exist
if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)

# Prepare a server socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
udpPingerSocket = socket(AF_INET, SOCK_DGRAM)
# udpPingerPort = 29001  # different port
# udpPingerSocket.bind(('', udpPingerPort))

SERVER_IP = "128.226.226.210"
SERVER_PORT = 12000
MAX_BLOCK_PERIOD = 1
PING_INTERVAL = 3
MAX_DURATION = 180

def handle_pinger():
    client_socket = udpPingerSocket
    client_socket.settimeout(MAX_BLOCK_PERIOD)
    
    start_program_time = time.time()
    sequence_number = 1

    # statistics
    total_rtt = 0
    min_rtt = float('inf')
    max_rtt = 0
    rtts_count = 0
    packet_loss_rate = 0
    avg_rtt = 0

    while time.time() - start_program_time < MAX_DURATION:
        # Create ping msg
        send_time = time.time()
        ping_msg = f"ping, {sequence_number}, {send_time}"
        
        try:
            # Print and send ping msg
            print(ping_msg)
            client_socket.sendto(ping_msg.encode(), (SERVER_IP, SERVER_PORT))
            
            # Print the server response/echo if there is one
            response, server_address = client_socket.recvfrom(1024)
            print(response.decode())
            
            # Calc and print RTT
            receive_time = time.time()
            rtt = receive_time - send_time
            print(f"Round Trip Time: {rtt} seconds\n")

            # Update statistics
            min_rtt = min(min_rtt, rtt)
            max_rtt = max(max_rtt, rtt)
            rtts_count += 1
            total_rtt += rtt

            # Calculate statistics
            num_lost = sequence_number - rtts_count
            packet_loss_rate = (num_lost / sequence_number) * 100
            # avoid arithmetic error
            if rtts_count > 0:
                avg_rtt = total_rtt / rtts_count
            else:
                avg_rtt = 0

            print("Ping statistics:")
            print(f"Minimum RTT: {min_rtt} seconds")
            print(f"Maximum RTT: {max_rtt} seconds")
            print(f"Total RTTs: {rtts_count}")
            print(f"Packet Loss Rate: {packet_loss_rate:.2f}%")
            print(f"Average RTTs: {avg_rtt} seconds\n")
            
        except timeout:
            print("Client ping timed out.\n")
        
        sequence_number += 1
        time.sleep(PING_INTERVAL)

    client_socket.close()

    # Print statistics
    print("Ping statistics:")
    print(f"Minimum RTT: {min_rtt} seconds")
    print(f"Maximum RTT: {max_rtt} seconds")
    print(f"Total RTTs: {rtts_count}")
    print(f"Packet Loss Rate: {packet_loss_rate:.2f}%")
    print(f"Average RTTs: {avg_rtt} seconds\n")


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
        proxyToWebSocket.connect(('128.226.226.210', serverPort))
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
    pinger_thread = threading.Thread(target=handle_pinger)
    pinger_thread.start()
    threads.append(pinger_thread)
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
