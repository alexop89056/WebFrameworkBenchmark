use axum::{routing::get, Json, Router};
use serde::Serialize;
use std::env;
use tokio::net::TcpListener;

#[derive(Serialize)]
struct HelloResponse {
    message: &'static str,
    framework: &'static str,
}

async fn hello() -> Json<HelloResponse> {
    Json(HelloResponse {
        message: "hello",
        framework: "rust-axum",
    })
}

async fn run() {
    let app = Router::new().route("/", get(hello));
    let listener = TcpListener::bind("0.0.0.0:8000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

fn main() {
    let workers = env::var("TOKIO_WORKERS")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .filter(|value| *value > 0)
        .unwrap_or(1);

    let runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(workers)
        .enable_all()
        .build()
        .unwrap();

    println!("Axum started with {workers} Tokio workers");
    runtime.block_on(run());
}
