#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../services/local-core-rs"
cargo run
