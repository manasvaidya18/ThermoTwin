"""Demo-clock labels: tick = one 10-minute logger reading."""

DAY = 1440


def clock_label(tick: int) -> str:
    minutes = (tick + 1) * 10
    day, rem = divmod(minutes, DAY)
    return f"Day {day + 1}, {rem // 60:02d}:{rem % 60:02d}"
