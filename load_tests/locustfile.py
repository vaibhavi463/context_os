from locust import HttpUser, task, between
import random


class ContextOSLoadUser(HttpUser):
    """
    Locust Load Testing User simulating operational queries,
    health checks, and telemetry requests against ContextOS API Gateway.
    """

    wait_time = between(1, 3)

    @task(4)
    def check_health_probes(self):
        self.client.get("/health")
        self.client.get("/ready")
        self.client.get("/live")

    @task(2)
    def query_admin_telemetry(self):
        self.client.get("/api/v1/admin/telemetry")

    @task(1)
    def execute_mock_investigation(self):
        payload = {
            "query": "High CPU utilization on DB Primary Pool due to unindexed vector search query spikes.",
            "max_history_turns": 5
        }
        self.client.post("/api/v1/investigations", json=payload)
