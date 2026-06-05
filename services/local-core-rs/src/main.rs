use std::{net::SocketAddr, sync::Arc};

use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use tokio::sync::RwLock;
use tower_http::cors::CorsLayer;

#[derive(Clone, Serialize, Deserialize)]
struct RuntimeState {
    emergency_stop_active: bool,
    last_reason: String,
}

#[derive(Serialize)]
struct HealthResponse {
    status: &'static str,
    service: &'static str,
}

#[derive(Deserialize)]
struct GuardRequest {
    command: String,
}

#[derive(Serialize)]
struct GuardResponse {
    allowed: bool,
    reason: String,
}

#[derive(Deserialize)]
struct StopRequest {
    command_text: String,
}

#[tokio::main]
async fn main() {
    let state = Arc::new(RwLock::new(RuntimeState {
        emergency_stop_active: false,
        last_reason: "ready".to_string(),
    }));

    let app = Router::new()
        .route("/health", get(health))
        .route("/state", get(get_state))
        .route("/guard/check", post(check_command))
        .route("/control/stop", post(stop))
        .route("/control/resume", post(resume))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], 9100));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    println!("jarvis-local-core listening on {}", addr);
    axum::serve(listener, app).await.unwrap();
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "online",
        service: "jarvis-local-core",
    })
}

async fn get_state(State(state): State<Arc<RwLock<RuntimeState>>>) -> Json<RuntimeState> {
    Json(state.read().await.clone())
}

async fn check_command(
    State(state): State<Arc<RwLock<RuntimeState>>>,
    Json(payload): Json<GuardRequest>,
) -> impl IntoResponse {
    let current = state.read().await;
    if current.emergency_stop_active {
        return (
            StatusCode::FORBIDDEN,
            Json(GuardResponse {
                allowed: false,
                reason: "Emergency stop is active.".to_string(),
            }),
        );
    }

    let denied_fragments = ["rm -rf", "shutdown", "reboot", "mkfs", "dd if="];
    let denied = denied_fragments
        .iter()
        .find(|fragment| payload.command.contains(*fragment));

    match denied {
        Some(fragment) => (
            StatusCode::FORBIDDEN,
            Json(GuardResponse {
                allowed: false,
                reason: format!("Command denied by local core guard: {}", fragment),
            }),
        ),
        None => (
            StatusCode::OK,
            Json(GuardResponse {
                allowed: true,
                reason: "Command passed local guard policy.".to_string(),
            }),
        ),
    }
}

async fn stop(
    State(state): State<Arc<RwLock<RuntimeState>>>,
    Json(payload): Json<StopRequest>,
) -> impl IntoResponse {
    if payload.command_text.trim() != "STOP JARVIS" {
        return (
            StatusCode::BAD_REQUEST,
            Json(GuardResponse {
                allowed: false,
                reason: "Invalid stop command.".to_string(),
            }),
        );
    }

    let mut current = state.write().await;
    current.emergency_stop_active = true;
    current.last_reason = "STOP JARVIS".to_string();

    (
        StatusCode::OK,
        Json(GuardResponse {
            allowed: false,
            reason: "Emergency stop activated.".to_string(),
        }),
    )
}

async fn resume(State(state): State<Arc<RwLock<RuntimeState>>>) -> impl IntoResponse {
    let mut current = state.write().await;
    current.emergency_stop_active = false;
    current.last_reason = "ready".to_string();

    (
        StatusCode::OK,
        Json(GuardResponse {
            allowed: true,
            reason: "Local core resumed.".to_string(),
        }),
    )
}
