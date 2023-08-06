"""Console script for planner."""
import sys
import os

# print(f"Trying to connect to a remote debugger..")
sys.path.append(os.path.dirname(__file__))
from . import wingdbstub

# import sys

# sys.exit(1)

# basic mycelium support
from pycelium.tools.cli.main import *

# from pycelium.tools.cli.config import config
# from pycelium.tools.cli.run import run

# import local submodules
# from pycelium.tools.cli.inventory import inventory


# import local submodules

from .inventory import inventory
from .plan import plan
from .real import real
from .roles import role
from .run import run
from .target import target
from .test import test
from .users import user
from .watch import watch
from .workspaces import workspace


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
