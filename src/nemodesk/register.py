# SPDX-License-Identifier: Apache-2.0
"""NemoDesk component registration.

The NeMo Agent Toolkit discovers components via the ``nat.components`` entry point
defined in pyproject.toml, which points here. Importing the tool modules below runs
their ``@register_function`` decorators so ``nat`` can resolve them from config YAML.
"""

# ruff: noqa: F401
from nemodesk.tools import classifier
from nemodesk.tools import escalation
from nemodesk.tools import kb_search
from nemodesk.tools import pii_redactor
