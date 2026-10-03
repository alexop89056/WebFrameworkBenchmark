FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod .
COPY main.go .
RUN go mod tidy
RUN go build -trimpath -ldflags="-s -w" -o /go-echo .

FROM alpine:3.22
COPY --from=build /go-echo /go-echo
EXPOSE 8000
ENTRYPOINT ["/go-echo"]
