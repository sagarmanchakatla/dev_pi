#!/bin/bash
# Analyze platform-api logs for the last hour

SINCE="${1:-1 hour ago}"
SERVICE="platform-api"

echo "=== Log Analysis: $SERVICE (since: $SINCE) ==="
echo ""

echo "--- Request Count ---"
journalctl -u $SERVICE --since "$SINCE" \
  | grep "request_completed" | wc -l

echo ""
echo "--- Error Count ---"
journalctl -u $SERVICE --since "$SINCE" -p err | wc -l

echo ""
echo "--- Status Code Distribution ---"
journalctl -u $SERVICE --since "$SINCE" \
  | grep -oP '"status_code": \d+' \
  | sort | uniq -c | sort -rn

echo ""
echo "--- Slowest Requests (>100ms) ---"
journalctl -u $SERVICE --since "$SINCE" \
  | grep "request_completed" \
  | grep -oP '"duration_ms": [\d.]+' \
  | awk -F': ' '$2 > 100 {print $2}' \
  | sort -rn | head -10

echo ""
echo "--- Recent Errors ---"
journalctl -u $SERVICE --since "$SINCE" -p err --no-pager | tail -20
