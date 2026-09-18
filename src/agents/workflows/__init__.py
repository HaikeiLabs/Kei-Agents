"""Harness-neutral workflow specifications.

Workflow modules are intentionally not eagerly imported here. The package
catalog imports their tool definitions after the core tool types exist; eager
imports would create a circular import during package initialization.
"""
