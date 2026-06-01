"""
AI Reasoning Project — Automated Ingestion Worker
Pulls external data to populate the World Model.
"""
class WebDataIngestor:
    def __init__(self, parser):
        self.parser = parser

    def ingest_url(self, url: str):
        """
        Fetches text, passes it through the parser to prevent CV-003, 
        and queues it for the graph.
        """
        raw_text = "Simulated extracted text from " + url
        node = self.parser.parse_to_node(raw_text, source_id="web_crawler")
        return node
