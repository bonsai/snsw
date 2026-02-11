from __future__ import annotations


class SnswError(RuntimeError):
    """Base error for snsw CLI."""


class MissingDependencyError(SnswError):
    pass


class ExternalToolError(SnswError):
    pass
