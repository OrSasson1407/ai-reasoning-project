class MetaCognitiveMonitor:
    def __init__(self):
        self.trigger_log = []

    def evaluate_inference_chain(self, inference_trace: dict, hops: int):
        """
        Evaluates inference against Meta-Cognitive Trigger Rules (MCT).
        """
        triggers = []
        
        if hops > 5:
            triggers.append("MCT-06: Long Chain Warning")
            
        if inference_trace.get("confidence", 1.0) < 0.4:
            triggers.append("MCT-04: Assumption Exposure")

        if inference_trace.get("mode") == "INDUCTIVE" and inference_trace.get("used_as_deductive_premise"):
            triggers.append("MCT-07: Inductive Overreach")
            
        if triggers:
            self.trigger_log.extend(triggers)
            
        return triggers
