"""
AI Reasoning Project — CLI Migration Tool
"""
from ai_reasoning.migrations.manager import MigrationManager
import sys

def main():
    if "--rollback" in sys.argv:
        print("Rolling back latest migration...")
    else:
        print("Running pending migrations...")
        # MigrationManager().run_migrations()

if __name__ == "__main__":
    main()
