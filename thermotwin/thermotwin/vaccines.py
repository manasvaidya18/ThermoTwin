"""Vaccine-aware alerts: the same temperature forecast matters more or less depending on what is in the fridge.

FREEZE_SENSITIVE lists vaccines damaged by freezing (aluminium-adjuvanted and some liquid vaccines); OPV, MR and BCG
tolerate freezing (OPV is even stored frozen). Compiled from WHO guidance on vaccine temperature sensitivity; verify
against the current WHO document and product inserts before field use.
"""
from __future__ import annotations

FREEZE_SENSITIVE = {
    "Pentavalent": True, "Hepatitis B": True, "DTP": True, "Td": True, "PCV": True, "IPV": True, "Rotavirus": True,
    "HPV": True, "OPV": False, "MR": False, "BCG": False,
}


def freeze_sensitive_stock(stock: list[str]) -> list[str]:
    return [v for v in stock if FREEZE_SENSITIVE.get(v, True)]   # unknown vaccines treated as sensitive (safe default)


def adjust_tier(tier: str, kind: str, stock: list[str]) -> tuple[str, str]:
    """Downgrade a freeze *forecast* to Advisory when nothing in the fridge is freeze-sensitive.

    Measured breaches (Critical) are never downgraded: the WHO alarm and the officer still decide.
    Returns (tier, note).
    """
    if kind != "freeze" or tier != "Early warning" or not stock:
        return tier, ""
    sensitive = freeze_sensitive_stock(stock)
    if sensitive:
        return tier, "Protect first: " + ", ".join(sensitive)
    return "Advisory", "No freeze-sensitive vaccines in this fridge"
