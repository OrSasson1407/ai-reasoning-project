from prometheus_client import Counter, Gauge, Histogram

class SystemMetrics:
    def __init__(self):
        # Counters
        self.nodes_created = Counter('nodes_created_total', 'Total number of knowledge nodes created')
        self.relations_created = Counter('relations_created_total', 'Total number of relations formed')
        self.contradictions_detected = Counter('contradictions_detected_total', 'Total contradictions caught by CCP')
        self.safety_violations = Counter('safety_violations_total', 'Total times VCL blocked a harmful node')
        
        # Gauges
        self.active_quarantines = Gauge('active_quarantines', 'Current number of quarantined nodes')
        self.average_confidence = Gauge('graph_average_confidence', 'Average confidence of all active nodes')
        
        # Histograms
        self.inference_latency = Histogram('inference_latency_seconds', 'Time taken to execute derive_node')

    def update_graph_metrics(self, graph):
        if not graph.nodes:
            return
        quarantined = sum(1 for n in graph.nodes.values() if n.quarantine_flag)
        self.active_quarantines.set(quarantined)
        
        active_nodes = [n for n in graph.nodes.values() if not n.quarantine_flag]
        if active_nodes:
            avg_conf = sum(n.confidence for n in active_nodes) / len(active_nodes)
            self.average_confidence.set(avg_conf)

# Global Metrics Instance
system_metrics = SystemMetrics()
