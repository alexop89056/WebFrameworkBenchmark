FROM alpine:3.22 AS build
RUN apk add --no-cache g++
WORKDIR /src
COPY main.cpp .
RUN g++ -O3 -static -s -std=c++17 main.cpp -o cpp-server

FROM alpine:3.22
COPY --from=build /src/cpp-server /cpp-server
EXPOSE 8000
ENTRYPOINT ["/cpp-server"]
