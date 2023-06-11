from socket import *
import threading
import time
import random
# In order to terminate the program
import sys

def server_echo(pingSocket):
    # timeout = 30 seconds
    pingSocket.settimeout(30.0)

    while True:
        try:
            # Generate random number in the range of 0 to 10
            rand = random.randint(0, 10)

            # Receive the client packet along with the address it is coming from
            message, address = pingSocket.recvfrom(1024)

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
            pingSocket.sendto(response, address)

        except timeout:
            print("Server echo timed out.")
            return



# Prepare a server socket
serverSocket = socket(AF_INET, SOCK_STREAM) #TCP welcoming server socket
serverPort = 28000
# binds the socket to the ip address and port number that the server will listen to for client requests
serverSocket.bind(('', serverPort))
# listens for incoming client requests but at most 1 queued connection
serverSocket.listen(1)
#array to track threads to ensure proper closing
threads = []



# Prepare a server socket
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
pingSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
pingSocket.bind(('', 12000)) # client/proxy will use this port



def handle_request(dataSocket):
    try:
        message = dataSocket.recv(2048).decode() #recv bytes and decode into string
        # Parse the HTTP request to get the requested file name
        filename = message.split()[1]
        f = open(filename[1:], 'rb') #filename, 'rb' or 'read binary' mode
        outputdata = f.read()
        f.close()

        # determine content type based on file extension
        content_type = ''
        if filename.endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.endswith('.html'):
            content_type = 'text/html'
        else:
            content_type = 'text/plain'

        # Send one HTTP header line into socket
        resp_header = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n".format(content_type, len(outputdata))
        dataSocket.send(resp_header.encode()) #encode to bytes
        # Send the content of the requested file into socket
        dataSocket.sendall(outputdata)

        print("server-response,200,{},{}".format(threading.current_thread().ident, int(time.time())))
        
        # Close the data socket
        dataSocket.close()
    except IOError:
        # Send HTTP response for file not found
        body404 = "<h1>404 Not Found</h1>" #response body content for 404
        #response header for 404
        resp_header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n".format(len(body404))
        dataSocket.send(resp_header.encode())
        dataSocket.send(body404.encode())

        print("server-response,404,{},{}".format(threading.current_thread().ident, int(time.time())))

        # Close the data socket
        dataSocket.close()


try:
    # Start the server echo thread
    ping_thread = threading.Thread(target=server_echo, args=(pingSocket,))
    ping_thread.start()
    threads.append(ping_thread)
    while True:
        # Establish the connection
        print('Web server is ready to serve...')

        #blocks until a client makes a connection
        dataSocket, addr = serverSocket.accept() #creates a new data socket

        # creates a new thread with thread constructor
        t = threading.Thread(target=handle_request, args=(dataSocket,))
        # starts the created thread
        t.start()
        threads.append(t)

except KeyboardInterrupt:
    #blocks and waits for all threads to complete before shutting down
    for t in threads:
        t.join()

    # Close server socket
    serverSocket.close()

    # Terminate the program after sending the corresponding data
    sys.exit()

