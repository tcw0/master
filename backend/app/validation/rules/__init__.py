"""
Auto-discovery of all validation rule modules.

Importing this package triggers every ``@validation_rule`` decorator
in the sub-modules, populating the global rule registry.
"""

import importlib

_rule_modules = [
    "01_glossary_rules",
    "02_event_storming_rules",
    "03_bounded_contexts_rules",
    "04_aggregates_rules",
    "05_architecture_rules",
    "cross_phase_rules",
]

for _module_name in _rule_modules:
    importlib.import_module(f"validation.rules.{_module_name}")
