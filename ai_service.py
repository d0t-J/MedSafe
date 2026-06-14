"""Compatibility layer for legacy imports.

The canonical implementation now lives under services.ai.service.
"""

from services.ai.service import analyze_drug, analyze_drugs, analyze_interaction

__all__ = ["analyze_drug", "analyze_interaction", "analyze_drugs"]
