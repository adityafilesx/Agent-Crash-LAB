#!/bin/bash
set -e
echo "Testing /health"
curl -s http://localhost:8000/health | grep -q "status" && echo "OK" || echo "FAIL"

echo "Testing /api/agents"
curl -s http://localhost:8000/api/agents | grep -q "demo-agent-001" && echo "OK" || echo "FAIL"

echo "Testing /api/agents/demo-agent-001"
curl -s http://localhost:8000/api/agents/demo-agent-001 | grep -q "demo-agent-001" && echo "OK" || echo "FAIL"

echo "Testing /api/scenarios"
curl -s http://localhost:8000/api/scenarios | grep -q "scenario-001" && echo "OK" || echo "FAIL"

echo "Testing /api/test-runs"
curl -s http://localhost:8000/api/test-runs | grep -q "id" && echo "OK" || echo "FAIL"

echo "Testing /api/test-runs/tr_a6e210e9983a"
curl -s http://localhost:8000/api/test-runs/tr_a6e210e9983a | grep -q "scenario_id" && echo "OK" || echo "FAIL"

