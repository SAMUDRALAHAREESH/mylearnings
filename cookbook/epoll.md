# Epoll

This guide explains a C program implementing a non-blocking TCP server using `epoll` for efficient event handling.

## 1. Program Overview
The program creates a TCP server that listens on port 8080, handles multiple client connections non-blockingly, and echoes received data back to clients using `epoll`.

## 2. Key Steps

### 2.1 Set Up Non-Blocking Socket
- Create a TCP socket and set it to non-blocking mode.
- Bind to port 8080 and listen for connections.

### 2.2 Initialize Epoll
- Create an `epoll` instance to monitor file descriptors.
- Add the server socket to `epoll` for incoming connections.

### 2.3 Handle Events
- Use `epoll_wait` to detect events (new connections or data).
- Accept new connections and set them to non-blocking.
- Add client sockets to `epoll` for data monitoring.
- Read and echo data from clients, handling connection closures.



## 3. Compile and Run
```bash
gcc -o epoll_server epoll_server.c
./epoll_server
```

**Output** (example):
```
Server listening on port 8080...
New connection: socket fd 4
Received from 4: Hello from client
Connection closed: socket fd 4
```