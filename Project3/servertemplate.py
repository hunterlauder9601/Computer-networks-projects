import random
import time
from socket import *

# Prepare a server socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 12000))

while True:
    # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)

    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)

    # If rand is less is than 4, we consider the packet lost and do not respond
    if rand < 4:
        continue

    # Otherwise, prepare the server response
    message_str = message.decode()
    message_parts = message_str.split(', ')

    # Get sequence number
    sequence_number = message_parts[1]

    # Create and send new message with the same sequence number
    # and the server's current timestamp
    response_str = f"echo, {sequence_number}, {time.time()}"
    response = response_str.encode()
    serverSocket.sendto(response, address)
