"""Allow running CLI as python -m wetwire_gitlab.cli."""

import sys

from .main import main

sys.exit(main())
