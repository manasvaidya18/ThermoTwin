"""Vaccine-aware alerts: the same forecast matters more or less depending on what is in the fridge.

The freeze-sensitivity catalogue comes from the vaccines table (db/seed/01_vaccines.sql).
Unknown vaccines are treated as freeze-sensitive (safe default).
"""
from __future__ import annotations


def freeze_sensitive_stock(stock: list[str], catalogue: dict[str, bool]) -> list[str]:
    return [v for v in stock if catalogue.get(v, True)]


def adjust_tier(tier: str, kind: str, stock: list[str], catalogue: dict[str, bool]) -> tuple[str, str]:
    """Downgrade a freeze *forecast* to Advisory when nothing in the fridge is freeze-sensitive.
    Measured breaches (Critical) are never downgraded. Returns (tier, note)."""
    if kind != "freeze" or tier != "Early warning" or not stock:
        return tier, ""
    sensitive = freeze_sensitive_stock(stock, catalogue)
    if sensitive:
        return tier, "Protect first: " + ", ".join(sensitive)
    return "Advisory", "No freeze-sensitive vaccines in this fridge"
