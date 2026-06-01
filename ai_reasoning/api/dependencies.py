"""
AI Reasoning Project — API Dependencies
Provides Singleton instances of the KnowledgeGraph and InferenceEngines to FastAPI routes.
"""
from fastapi import Depends
from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.inference.engine import InferenceEngine
from ai_reasoning.meta.horizon import EpistemicHorizon

# In a production app, these would be backed by the database adapters
# For the architectural framework, we initialize the singletons here.
global_graph = KnowledgeGraph()
global_horizon = EpistemicHorizon()
global_inference_engine = InferenceEngine(global_graph)

def get_graph() -> KnowledgeGraph:
    return global_graph

def get_horizon() -> EpistemicHorizon:
    return global_horizon

def get_inference_engine() -> InferenceEngine:
    return global_inference_engine
