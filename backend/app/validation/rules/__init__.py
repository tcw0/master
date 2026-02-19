"""
Auto-discovery of all validation rule modules.

Importing this package triggers every ``@validation_rule`` decorator
in the sub-modules, populating the global rule registry.
"""

from validation.rules import (  # noqa: F401
    glossary_rules,
    event_storming_rules,
    bounded_contexts_rules,
    aggregates_rules,
    architecture_rules,
    cross_phase_rules,
)
