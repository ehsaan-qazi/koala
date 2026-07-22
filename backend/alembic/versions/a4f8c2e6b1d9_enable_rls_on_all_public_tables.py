"""enable_rls_on_all_public_tables

Revision ID: a4f8c2e6b1d9
Revises: 381f41da975a
Create Date: 2026-07-22

Security fix: enables Row-Level Security (RLS) on every table in the public
schema and adds a RESTRICTIVE deny-all policy for the Supabase ``anon`` role.

Background
----------
Tables created via Alembic / SQLAlchemy do NOT have RLS enabled by default.
Supabase exposes every public-schema table through its PostgREST REST API. With
RLS disabled anyone who has the project URL and the public ``anon`` key can read,
write, and delete all rows — bypassing the FastAPI backend entirely.

Why this migration is sufficient (and not over-engineered)
----------------------------------------------------------
* The FastAPI backend connects to Postgres using the DATABASE_URL which resolves
  to the *service role* (superuser). PostgreSQL superusers always bypass RLS, so
  zero existing backend behaviour is affected.
* The Supabase PostgREST layer runs as the ``anon`` or ``authenticated`` role.
  With RLS enabled and **no permissive policy** for those roles, all access is
  denied by default. The explicit RESTRICTIVE policy added here makes that intent
  visible in ``pg_policies`` and survives future permissive-policy additions.
* No application code, schemas, or routes need to change.

Downgrade is fully reversible: policies are dropped and RLS is disabled.

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a4f8c2e6b1d9"
down_revision: Union[str, None] = "381f41da975a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ---------------------------------------------------------------------------
# All tables that exist in the public schema as of revision 381f41da975a.
# Maintain this list whenever a new migration creates a public table.
# ---------------------------------------------------------------------------
_TABLES = [
    "users",
    "courses",
    "goals",
    "goal_courses",
    "streak_daily_log",
    "streaks",
    "subscriptions",
    "documents",
    "roadmap_nodes",
    "self_assessment_logs",
    "topics",
    "topic_completions",
    "notes",
    "note_links",
    "gpa_entries",
]

# Policy name used in both upgrade and downgrade so the strings stay in sync.
_POLICY_NAME = "deny_anon_all"


def upgrade() -> None:
    """
    Enable RLS and add a RESTRICTIVE deny-all policy for the ``anon`` role on
    every public table.

    RESTRICTIVE policies are combined with AND logic against any permissive
    policies, so even if a permissive policy is accidentally added later it
    cannot override this explicit deny for the anon role.
    """
    for table in _TABLES:
        # Step 1: Enable RLS.  With RLS on and no permissive policy, the default
        # behaviour already denies all non-superuser access.  We add an explicit
        # RESTRICTIVE policy below to make the intent unambiguous.
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")

        # Step 2: Add a RESTRICTIVE deny-all policy for the anon role.
        # USING (false) means the WHERE clause never matches any row → full deny.
        op.execute(
            f"""
            CREATE POLICY {_POLICY_NAME}
                ON public.{table}
                AS RESTRICTIVE
                TO anon
                USING (false);
            """
        )


def downgrade() -> None:
    """
    Drop the deny-anon policies and disable RLS on every public table,
    restoring the pre-fix state.
    """
    for table in _TABLES:
        op.execute(
            f"DROP POLICY IF EXISTS {_POLICY_NAME} ON public.{table};"
        )
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")
