"""CLI command handlers."""

from wetwire_gitlab.cli.commands.build import run_build
from wetwire_gitlab.cli.commands.design import run_design
from wetwire_gitlab.cli.commands.graph import run_graph
from wetwire_gitlab.cli.commands.import_cmd import run_import
from wetwire_gitlab.cli.commands.init import run_init
from wetwire_gitlab.cli.commands.lint import run_lint
from wetwire_gitlab.cli.commands.list_cmd import run_list
from wetwire_gitlab.cli.commands.test import run_test
from wetwire_gitlab.cli.commands.validate import run_validate
from wetwire_gitlab.cli.commands.version import run_version

__all__ = [
    "run_build",
    "run_design",
    "run_graph",
    "run_import",
    "run_init",
    "run_lint",
    "run_list",
    "run_test",
    "run_validate",
    "run_version",
]
