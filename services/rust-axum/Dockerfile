FROM rust:1.85-alpine AS build
RUN apk add --no-cache musl-dev
WORKDIR /src
COPY Cargo.toml .
COPY src ./src
RUN cargo build --release

FROM alpine:3.22
COPY --from=build /src/target/release/rust-axum-bench /rust-axum-bench
EXPOSE 8000
ENTRYPOINT ["/rust-axum-bench"]
