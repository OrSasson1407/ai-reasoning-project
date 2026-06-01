"""
AI Reasoning Project — Migration Manager
Executes versioned migrations to ensure state consistency.
"""
import importlib.util
import os

class MigrationManager:
    def __init__(self, db_adapter):
        self.db = db_adapter
        self.version_table = "schema_version"

    def run_migrations(self):
        """Applies all pending migrations in order."""
        version_dir = "ai_reasoning/migrations/versions"
        migrations = sorted([f for f in os.listdir(version_dir) if f.endswith(".py")])
        
        for mig in migrations:
            print(f"Applying migration: {mig}")
            # Dynamic import and execution
            spec = importlib.util.spec_from_file_location("mig", os.path.join(version_dir, mig))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.upgrade()

if __name__ == "__main__":
    # In practice, initialize adapter and run
    print("Migration suite initialized.")
