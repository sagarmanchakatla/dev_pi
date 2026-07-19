# Deployment Runbook

## Standard Deployment

1. Ensure all tests pass on main branch
2. Create annotated release tag
   git tag -a vX.Y.Z -m "Release notes"
   git push origin vX.Y.Z
3. On server, pull latest code
4. Restart service
   sudo systemctl restart platform-api
5. Verify health check
   curl http://localhost:8000/health

## Rollback

1. Identify last known good tag
   git tag -l
2. Check out that tag
   git checkout vX.Y.Z
3. Restart service
   sudo systemctl restart platform-api
4. Verify health check

## Contacts
- On-call: check PagerDuty

## Monitoring

Grafana dashboard: http://raspberrypi.local:3000
Prometheus: http://raspberrypi.local:9090
Default credentials: admin / changeme (change in production)

Key dashboards:
  Platform API Overview - request rate, latency, memory
