"""
AI Reasoning Project — Trigger EBD Evaluation
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_reasoning.evaluation.benchmarks import BenchmarkingEngine
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.meta.horizon import EpistemicHorizon

def main():
    print("Starting Post-Consolidation Evaluation (EBD)...")
    graph = KnowledgeGraph()
    horizon = EpistemicHorizon()
    engine = BenchmarkingEngine(graph, horizon)
    
    report = engine.generate_ebd_report()
    print(report)

if __name__ == "__main__":
    main()
