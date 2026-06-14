"""Compatibility layer for legacy imports.

The canonical implementation now lives under services.drug.service.
"""

from services.drug.service import (
    fetch_fda_label,
    fetch_multiple_drugs,
    normalize_drug_name,
    search_fda,
)

__all__ = [
    "normalize_drug_name",
    "search_fda",
    "fetch_fda_label",
    "fetch_multiple_drugs",
]
