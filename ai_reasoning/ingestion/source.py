class SourceValidator:
    """Enforces Rule DI-04: Source Required."""
    def __init__(self):
        self.known_sources = set(["human_operator", "system_sensor_1"])

    def validate_source(self, source_id: str) -> bool:
        return source_id in self.known_sources
