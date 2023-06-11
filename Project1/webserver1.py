from socket import *

# In order to terminate the program
import sys

# Prepare a server socket
serverSocket = socket(AF_INET, SOCK_STREAM) #TCP welcoming server socket
serverPort = 28000
# binds the socket to the ip address and port number that the server will listen to for client requests
serverSocket.bind(('', serverPort))
# listens for incoming client requests but at most one queued connection
serverSocket.listen(1)

while True:
    # Establish the connection
    print('Ready to serve...')

    #blocks until a client makes a connection
    connectionSocket, addr = serverSocket.accept() #creates a new data socket

    try:
        message = connectionSocket.recv(512).decode() #recv bytes and decode into string
        # Parse the HTTP request to get the requested file name
        filename = message.split()[1]
        f = open(filename[1:], 'r', encoding='utf-8-sig') # filename, read, encoding
        outputdata = f.read()
        f.close()

        # Send one HTTP header line into socket
        resp_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n".format(len(outputdata))
        connectionSocket.send(resp_header.encode()) #encode to bytes

        # Send the content of the requested file into socket
        for i in range(0, len(outputdata)): #sends one character at a time
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        
        # Close the data socket
        connectionSocket.close()
    except IOError:
        # Send HTTP response for file not found
        body404 = "<h1>404 Not Found</h1>" #response body content for 404
        #response header for 404
        resp_header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n".format(len(body404))
        connectionSocket.send(resp_header.encode())
        connectionSocket.send(body404.encode())

        # Close the data socket
        connectionSocket.close()

# Close server socket
serverSocket.close()

# Terminate the program after sending the corresponding data
sys.exit()
