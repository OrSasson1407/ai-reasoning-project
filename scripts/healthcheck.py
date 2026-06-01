"""
AI Reasoning Project — System Integrity Healthcheck
Used by Kubernetes Liveness/Readiness probes to ensure the architecture hasn't crashed.
"""
import httpx
import sys

def run_healthcheck():
    try:
        r = httpx.get("http://localhost:8000/health", timeout=5.0)
        if r.status_code == 200:
            print("Core Engine: ONLINE")
            sys.exit(0)
        else:
            print(f"Core Engine: DEGRADED ({r.status_code})")
            sys.exit(1)
    except httpx.ConnectError:
        print("Core Engine: OFFLINE")
        sys.exit(1)

if __name__ == "__main__":
    run_healthcheck()
