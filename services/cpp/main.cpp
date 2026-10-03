#include <arpa/inet.h>
#include <cstring>
#include <cstdlib>
#include <netinet/in.h>
#include <sys/socket.h>
#include <thread>
#include <vector>
#include <unistd.h>

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int reuse = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8000);
    bind(server_fd, reinterpret_cast<sockaddr*>(&address), sizeof(address));
    listen(server_fd, 256);

    const char response[] =
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 44\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{\"message\":\"hello\",\"framework\":\"cpp-native\"}";

    int workers = 1;
    if (const char* value = std::getenv("CPP_WORKERS")) {
        workers = std::atoi(value);
        if (workers < 1) workers = 1;
    }

    auto serve = [&]() {
        while (true) {
            int client = accept(server_fd, nullptr, nullptr);
            if (client < 0) continue;
            char buffer[1024];
            recv(client, buffer, sizeof(buffer), 0);
            send(client, response, sizeof(response) - 1, 0);
            close(client);
        }
    };

    std::vector<std::thread> threads;
    threads.reserve(workers);
    for (int worker = 0; worker < workers; ++worker) {
        threads.emplace_back(serve);
    }
    for (auto& thread : threads) thread.join();
}
