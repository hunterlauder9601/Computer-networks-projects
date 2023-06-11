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

sys.exit()

