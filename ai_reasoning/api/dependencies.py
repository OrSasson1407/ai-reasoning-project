from ai_reasoning.core.graph import KnowledgeGraph
from ai_reasoning.inference.engine import InferenceEngine
from ai_reasoning.alignment.vcl import ValuesConstraintLayer
from ai_reasoning.ccp.detector import ContradictionDetector
from ai_reasoning.storage.neo4j_adapter import Neo4jAdapter
from ai_reasoning.storage.audit import StrictAuditLogger
from ai_reasoning.meta.horizon import EpistemicHorizon
from ai_reasoning.meta.reflection import MetaReflectionEngine

# Global Singletons
global_graph = KnowledgeGraph()
global_engine = InferenceEngine(global_graph)
global_vcl = ValuesConstraintLayer()
global_ccp = ContradictionDetector(global_graph)
global_db = Neo4jAdapter()
global_audit = StrictAuditLogger()
global_horizon = EpistemicHorizon()
global_reflection = MetaReflectionEngine(global_graph)

def get_graph() -> KnowledgeGraph: return global_graph
def get_engine() -> InferenceEngine: return global_engine
def get_vcl() -> ValuesConstraintLayer: return global_vcl
def get_ccp() -> ContradictionDetector: return global_ccp
def get_db() -> Neo4jAdapter: return global_db
def get_audit() -> StrictAuditLogger: return global_audit
def get_horizon() -> EpistemicHorizon: return global_horizon
def get_reflection() -> MetaReflectionEngine: return global_reflection
