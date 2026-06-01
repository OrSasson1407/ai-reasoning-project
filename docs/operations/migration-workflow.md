# Migration Workflow
All schema changes must follow the versioned migration pattern in `ai_reasoning/migrations/`.

1. Generate new migration script.
2. Run `python scripts/migrate.py` in dev environment.
3. Verify integrity using `pytest`.
4. Commit migration script to VCS.
