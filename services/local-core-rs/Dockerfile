FROM rust:1.79 as builder

WORKDIR /app
COPY services/local-core-rs/Cargo.toml Cargo.toml
COPY services/local-core-rs/src src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/jarvis-local-core /usr/local/bin/jarvis-local-core
CMD ["jarvis-local-core"]
