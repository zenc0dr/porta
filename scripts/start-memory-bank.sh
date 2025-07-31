#!/bin/bash
export MEMORY_BASE_PATH="$(pwd)/memory-bank-data"
mkdir -p "$MEMORY_BASE_PATH"
node ./mcp/memory_bank_engine/dist/memory-bank.js
