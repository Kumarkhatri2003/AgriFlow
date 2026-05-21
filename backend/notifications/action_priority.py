"""Priority levels derived from days until an action is due."""


def priority_from_days_until(days_until: int) -> str:
    """
    Map days until action date to notification priority.

    critical → overdue (days_until < 0)
    urgent   → due today (days_until == 0)
    high     → 1–2 days
    medium   → 3–4 days
    low      → 5+ days away
    """
    if days_until < 0:
        return 'critical'
    if days_until == 0:
        return 'urgent'
    if days_until <= 2:
        return 'high'
    if days_until <= 4:
        return 'medium'
    return 'low'
