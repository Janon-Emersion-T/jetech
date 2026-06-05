#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../services/automation-node"
node src/server.js
