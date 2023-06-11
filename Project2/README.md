# Binghamton University, Spring 2023

## CS428/528 Project-2: Proxy Server

### SUMMARY

For part 1, we implemented a proxy server which forwards requests received from the client to the web
server and then forwards responses received from the web server back to the client.

For part 2, we implemented a proxy server which functions the same as the part 1 proxy server
except it caches the receieved responses from the web server if they are not already cached and it forwards cached responses
if the request matches the request of a previously cached response.

### NOTES, KNOWN BUGS, AND/OR INCOMPLETE PARTS

N/A

### REFERENCES

https://www.programiz.com/python-programming/methods/built-in/open 
From slides: "Example app: TCP server" 
https://www.geeksforgeeks.org/socket-programming-multi-threading-python/ 
https://docs.python.org/3/library/threading.html
https://alexanderell.is/posts/simple-cache-server-in-python/

### INSTRUCTIONS

Hosting the proxy server and web server on one computer:

run proxyserver1.py and webserver.py then send request to proxyserver1 from client

It can be accessed using the following format in browser: 
http://(ProxyServerIP):29000/Project2-ProxyServer.pdf
http://(ProxyServerIP):29000/home.html

The same can be used for proxyserver2

Hosting on two different computers:

Inside of the proxyserver file change localhost to the webserver's IP address. 
For both, these lines can be found on:
proxyserver1 line 20
proxyserver2 line 56

After this change both can be run using python and then accessed just as before.

### SUBMISSION

I have done this assignment completely on my own. I have not copied it, nor have I given my solution to anyone else. I understand that if I am involved in plagiarism or cheating I will have to sign an official form that I have cheated and that this form will be stored in my official university record. I also understand that I will receive a grade of "0" for the involved assignment and my grade will be reduced by one level (e.g., from "A" to "A-" or from "B+" to "B") for my first offense, and that I will receive a grade of "F" for the course for any additional offense of any kind.

By signing my name below and submitting the project, I confirm the above statement is true and that I have followed the course guidelines and policies.

Submission date: 3/25/23

Team member 1 name: Hunter Lauder

Team member 2 name: Anthony Goncalves

