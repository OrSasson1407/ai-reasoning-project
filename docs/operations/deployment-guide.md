# Deployment Strategy
The system is designed for containerized deployment (Docker/Kubernetes).

- **Core Engine:** Stateless inference microservice.
- **API Gateway:** Edge enforcement (AIC validation).
- **State:** MongoDB (Nodes/Relations) + PostgreSQL (Audit Logs).
- **Telemetry:** Prometheus + Grafana (Monitoring ECE and contract violations).
