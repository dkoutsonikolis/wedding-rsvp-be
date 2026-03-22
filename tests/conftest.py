"""
Root conftest.py - imports all fixtures to make them available everywhere.

All fixtures are organized in separate modules under tests/fixtures/
and imported here so they're accessible to all tests.
"""

import os

# Auth routes share one client IP in ASGITransport tests; relax limits before `main` import.
os.environ["RATE_LIMIT_AUTH_REGISTER"] = "10000/minute"
os.environ["RATE_LIMIT_AUTH_LOGIN"] = "10000/minute"
os.environ["RATE_LIMIT_AUTH_REFRESH"] = "10000/minute"

# Import all fixtures to make them available at the top level
from tests.fixtures.client import *  # noqa: F403, F401
from tests.fixtures.database import *  # noqa: F403, F401
from tests.fixtures.messages import *  # noqa: F403, F401
from tests.fixtures.users import *  # noqa: F403, F401
