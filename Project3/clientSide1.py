import sys
import time
from socket import *

SERVER_IP = "128.226.226.210"
SERVER_PORT = 12000
MAX_BLOCK_PERIOD = 1
PING_INTERVAL = 3
MAX_DURATION = 180

# Prepare a server socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(MAX_BLOCK_PERIOD)

start_program_time = time.time()
sequence_number = 1

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
        
    except timeout:
        print("Client ping timed out.\n")
    
    sequence_number += 1
    time.sleep(PING_INTERVAL)

client_socket.close()
sys.exit()
