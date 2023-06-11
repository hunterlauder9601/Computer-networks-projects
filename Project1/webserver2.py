from socket import *
import threading

# In order to terminate the program
import sys

# Prepare a server socket
serverSocket = socket(AF_INET, SOCK_STREAM) #TCP welcoming server socket
serverPort = 28000
# binds the socket to the ip address and port number that the server will listen to for client requests
serverSocket.bind(('', serverPort))
# listens for incoming client requests but  at most 5 queued connections
serverSocket.listen(1)

def handle_request(connectionSocket):
    try:
        message = connectionSocket.recv(2048).decode() #recv bytes and decode into string
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
        connectionSocket.send(resp_header.encode()) #encode to bytes
        # Send the content of the requested file into socket
        connectionSocket.sendall(outputdata)

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

while True:
        # Establish the connection
        print('Ready to serve...')

        #blocks until a client makes a connection
        connectionSocket, addr = serverSocket.accept() #creates a new data socket

        # creates a new thread with thread constructor
        t = threading.Thread(target=handle_request, args=(connectionSocket, ))
        # starts the created thread
        t.start()

# Close server socket
serverSocket.close()

# Terminate the program after sending the corresponding data
sys.exit()
