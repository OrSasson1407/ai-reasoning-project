"""
API Gateway — Structured Access Logging
Logs all ingress/egress traffic at the edge.
"""
import logging
import sys

def setup_gateway_logger():
    logger = logging.getLogger("api_gateway")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "api-gateway", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

gateway_logger = setup_gateway_logger()
