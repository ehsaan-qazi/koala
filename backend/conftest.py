"""Pytest configuration.

Ensures the backend directory is on ``sys.path`` so that ``import app`` resolves
when pytest is run from the ``backend/`` working directory (as the CI does).
Without this, pytest's default import mode only adds ``backend/tests/`` to the
path, so ``app`` (in ``backend/app``) is not importable.
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
