"""
AI Reasoning Project — EBD Self-Evaluation Report Generator
Sourced from: EBD v1.0
"""

from datetime import datetime, timezone
from ai_reasoning.meta.horizon import EpistemicHorizon
from ai_reasoning.core.graph import KnowledgeGraph

class BenchmarkingEngine:
    def __init__(self, graph: KnowledgeGraph, horizon: EpistemicHorizon):
        self.graph = graph
        self.horizon = horizon

    def generate_ebd_report(self) -> str:
        """Generates the exact EBD post-consolidation report specified in the architecture."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        stats = self.graph.stats()
        
        report = f"""
        SELF-EVALUATION REPORT [post-consolidation]
        ──────────────────────────────────────────────────────────────────
        Period             : {now}
        Total Nodes Active : {stats['total_nodes']}
        Active Contradicts : {stats['active_contradictions']}
        Quarantined Nodes  : {stats['quarantined_nodes']}

        ACCURACY BY DOMAIN
        """
        for domain, score in self.horizon.domain_calibration.items():
            status = self.horizon.check_horizon(domain)["horizon_status"]
            report += f"  {domain:<27}: {score:.2f}  [{status}]\n"

        report += """
        RECOMMENDED ACTIONS
          → Apply confidence scalar updates based on horizon status.
          → Resolve Level 1 HALT contradictions pending in CCP.
        ──────────────────────────────────────────────────────────────────
        """
        return report
