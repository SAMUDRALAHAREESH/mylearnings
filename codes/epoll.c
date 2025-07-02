#include <stdio.h>
#include <stdlib.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#define MAX_EVENTS 10
#define PORT 8080

// Set socket to non-blocking mode
void set_nonblocking(int sockfd) {
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);
}

int main() {
    int server_fd, new_socket, epoll_fd, num_events;
    struct epoll_event event, events[MAX_EVENTS];
    struct sockaddr_in address;
    int addrlen = sizeof(address);

    // Create server socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    set_nonblocking(server_fd);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 10) < 0) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }

    // Create epoll instance
    epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("epoll_create1 failed");
        exit(EXIT_FAILURE);
    }

    // Add server socket to epoll
    event.events = EPOLLIN; 
    event.data.fd = server_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &event) == -1) {
        perror("epoll_ctl failed");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", PORT);

    while (1) {
        num_events = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (num_events == -1) {
            perror("epoll_wait failed");
            exit(EXIT_FAILURE);
        }

        // To Handle the events
        for (int i = 0; i < num_events; i++) {
            if (events[i].data.fd == server_fd) {
                // New connection
                new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen);
                if (new_socket == -1) {
                    perror("accept failed");
                    continue;
                }

                // Set new socket to non-blocking
                set_nonblocking(new_socket);

                // Added new socket to epoll
                event.events = EPOLLIN | EPOLLET; 
                event.data.fd = new_socket;
                if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, new_socket, &event) == -1) {
                    perror("epoll_ctl failed");
                    close(new_socket);
                    continue;
                }

                printf("New connection: socket fd %d\n", new_socket);
            } else {
                char buffer[1024];
                int fd = events[i].data.fd;
                ssize_t bytes_read;

                while (1) {
                    bytes_read = read(fd, buffer, sizeof(buffer));
                    if (bytes_read == -1) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) {
                            // No more data to read
                            break;
                        }
                        perror("read failed");
                        close(fd);
                        break;
                    } else if (bytes_read == 0) {
                        // Connection closed
                        printf("Connection closed: socket fd %d\n", fd);
                        close(fd);
                        break;
                    } else {
                        // Echo data 
                        buffer[bytes_read] = '\0';
                        printf("Received from %d: %s\n", fd, buffer);
                        write(fd, buffer, bytes_read);
                    }
                }
            }
        }
    }
    close(server_fd);
    close(epoll_fd);
    return 0;
}