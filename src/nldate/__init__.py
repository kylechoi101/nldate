import re
from datetime import date, timedelta

MONTH_NAMES = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "tues": 1,
    "wed": 2,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


def _strip_ordinal(s: str) -> str:
    return re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", s)


def _parse_number_word(s: str) -> int | None:
    words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }
    return words.get(s.lower())


def _parse_simple_number(s: str) -> int | None:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    return _parse_number_word(s)


_UNIT_DAYS = {
    "day": 1,
    "days": 1,
    "week": 7,
    "weeks": 7,
}


def _apply_offset(d: date, years: int = 0, months: int = 0, days: int = 0) -> date:
    if years or months:
        total_months = d.month - 1 + months + years * 12
        target_year = d.year + total_months // 12
        target_month = total_months % 12 + 1
        target_day = min(
            d.day,
            [
                31,
                29
                if target_year % 4 == 0
                and (target_year % 100 != 0 or target_year % 400 == 0)
                else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][target_month - 1],
        )
        d = date(target_year, target_month, target_day)
    if days:
        d += timedelta(days=days)
    return d


def _parse_absolute_date(s: str) -> date | None:
    s = s.strip()

    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.match(r"(\d{4})[/.](\d{1,2})[/.](\d{1,2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.match(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))

    s_clean = _strip_ordinal(s)
    m = re.match(r"(?i)([a-z]+)\s+(\d{1,2}),?\s*(\d{4})$", s_clean)
    if m:
        month_name = m.group(1).lower()
        if month_name in MONTH_NAMES:
            return date(int(m.group(3)), MONTH_NAMES[month_name], int(m.group(2)))

    m = re.match(r"(?i)(\d{1,2})\s+([a-z]+)\s+(\d{4})$", s_clean)
    if m:
        month_name = m.group(2).lower()
        if month_name in MONTH_NAMES:
            return date(int(m.group(3)), MONTH_NAMES[month_name], int(m.group(1)))

    return None


def _parse_date_expr(s: str, today: date) -> date | None:
    s = s.strip().lower()
    if s in ("today",):
        return today
    if s in ("tomorrow",):
        return today + timedelta(days=1)
    if s in ("yesterday",):
        return today - timedelta(days=1)

    return _parse_absolute_date(s)


def _next_weekday(from_date: date, target_weekday: int) -> date:
    days_ahead = target_weekday - from_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return from_date + timedelta(days=days_ahead)


def _last_weekday(from_date: date, target_weekday: int) -> date:
    days_behind = from_date.weekday() - target_weekday
    if days_behind <= 0:
        days_behind += 7
    return from_date - timedelta(days=days_behind)


def _this_weekday(from_date: date, target_weekday: int) -> date:
    if from_date.weekday() == target_weekday:
        return from_date
    return _next_weekday(from_date, target_weekday)


def _parse_relative_parts(s: str) -> list[tuple[str, int]] | None:
    s = s.strip().lower()
    parts = re.split(r"\s+and\s+", s)
    result = []
    for part in parts:
        m = re.match(r"(\d+)\s+(year|years|month|months|week|weeks|day|days)", part)
        if m:
            result.append((m.group(2), int(m.group(1))))
            continue
        m = re.match(r"a\s+(year|month|week|day)", part)
        if m:
            result.append((m.group(1), 1))
            continue
        return None
    return result if result else None


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = _strip_ordinal(s.strip())

    weekday_result = _try_weekday_expression(s, today)
    if weekday_result is not None:
        return weekday_result

    result = _try_relative_expression(s, today)
    if result is not None:
        return result

    result = _try_compound_relative_expression(s, today)
    if result is not None:
        return result

    result = _try_duration_from_now(s, today)
    if result is not None:
        return result

    result = _try_simple_date_expr(s, today)
    if result is not None:
        return result

    result = _try_bare_relative_to_date(s, today)
    if result is not None:
        return result

    absolute = _parse_absolute_date(s)
    if absolute is not None:
        return absolute

    msg = f"Could not parse date: {s}"
    raise ValueError(msg)


def _try_weekday_expression(s: str, today: date) -> date | None:
    s_lower = s.lower()
    m = re.match(r"(next|last|this)\s+([a-z]+)", s_lower)
    if m:
        prefix = m.group(1)
        wd_name = m.group(2)
        if wd_name in WEEKDAYS:
            wd = WEEKDAYS[wd_name]
            if prefix == "next":
                return _next_weekday(today, wd)
            elif prefix == "last":
                return _last_weekday(today, wd)
            elif prefix == "this":
                return _this_weekday(today, wd)

    if s_lower in WEEKDAYS:
        wd = WEEKDAYS[s_lower]
        if today.weekday() == wd:
            return today
        return _next_weekday(today, wd)

    return None


def _try_relative_expression(s: str, today: date) -> date | None:
    s_lower = s.lower()
    m = re.match(
        r"in\s+(?:a\s+)?(year|years|month|months|week|weeks|day|days)$", s_lower
    )
    if m:
        unit = m.group(1)
        offset = _UNIT_DAYS.get(unit, 0)
        if offset:
            return today + timedelta(days=offset)
        if unit in ("month", "months"):
            return _apply_offset(today, months=1)
        if unit in ("year", "years"):
            return _apply_offset(today, years=1)

    m = re.match(
        r"(\d+)\s+(year|years|month|months|week|weeks|day|days)\s+(from now|ago)",
        s_lower,
    )
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        direction = m.group(3)
        sign = -1 if direction == "ago" else 1
        offset_days = _UNIT_DAYS.get(unit, 0)
        if offset_days:
            return today + timedelta(days=sign * n * offset_days)
        if unit in ("month", "months"):
            return _apply_offset(today, months=sign * n)
        if unit in ("year", "years"):
            return _apply_offset(today, years=sign * n)

    m = re.match(
        r"(?:in\s+)?(\d+)\s+(year|years|month|months|week|weeks|day|days)$",
        s_lower,
    )
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        offset_days = _UNIT_DAYS.get(unit, 0)
        if offset_days:
            return today + timedelta(days=n * offset_days)
        if unit in ("month", "months"):
            return _apply_offset(today, months=n)
        if unit in ("year", "years"):
            return _apply_offset(today, years=n)

    m = re.match(
        r"(\d+)\s+(year|years|month|months|week|weeks|day|days)\s+ago$",
        s_lower,
    )
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        offset_days = _UNIT_DAYS.get(unit, 0)
        if offset_days:
            return today - timedelta(days=n * offset_days)
        if unit in ("month", "months"):
            return _apply_offset(today, months=-n)
        if unit in ("year", "years"):
            return _apply_offset(today, years=-n)

    return None


def _try_compound_relative_expression(s: str, today: date) -> date | None:
    s_lower = s.lower()
    m = re.match(
        r"((?:\d+\s+(?:year|years|month|months|week|weeks|day|days)\s*(?:and\s*)?)+)"
        r"(before|after)\s+(.+)",
        s_lower,
    )
    if not m:
        return None

    offset_str = m.group(1)
    direction = m.group(2)
    ref_str = m.group(3)

    ref_date = _parse_date_expr(ref_str, today)
    if ref_date is None:
        return None

    sign = -1 if direction == "before" else 1
    years = months = days = 0
    for unit_part in re.findall(
        r"(\d+)\s+(year|years|month|months|week|weeks|day|days)", offset_str
    ):
        n = int(unit_part[0])
        u = unit_part[1]
        if u in ("year", "years"):
            years += sign * n
        elif u in ("month", "months"):
            months += sign * n
        elif u in ("week", "weeks"):
            days += sign * n * 7
        elif u in ("day", "days"):
            days += sign * n

    return _apply_offset(ref_date, years=years, months=months, days=days)


def _try_duration_from_now(s: str, today: date) -> date | None:
    s_lower = s.lower()

    m = re.match(
        r"(\d+)\s+(day|days)\s+(before|after)\s+(today|tomorrow|yesterday)",
        s_lower,
    )
    if m:
        n = int(m.group(1))
        direction = m.group(3)
        ref = _parse_date_expr(m.group(4), today)
        if ref is None:
            return None
        if direction == "before":
            return ref - timedelta(days=n)
        return ref + timedelta(days=n)

    return None


def _try_simple_date_expr(s: str, today: date) -> date | None:
    s_lower = s.strip().lower()
    if s_lower in ("today", "tomorrow", "yesterday"):
        return _parse_date_expr(s, today)
    return None


def _try_bare_relative_to_date(s: str, today: date) -> date | None:
    s_lower = s.lower()

    m = re.match(
        r"(\d+)\s+(year|years|month|months|week|weeks|day|days)\s+(before|after)\s+(.+)",
        s_lower,
    )
    if not m:
        return None

    n = int(m.group(1))
    unit = m.group(2)
    direction = m.group(3)
    ref_str = m.group(4)

    ref_date = _parse_date_expr(ref_str, today)
    if ref_date is None:
        return None

    sign = -1 if direction == "before" else 1
    offset_days = _UNIT_DAYS.get(unit, 0)
    if offset_days:
        return ref_date + timedelta(days=sign * n * offset_days)
    if unit in ("month", "months"):
        return _apply_offset(ref_date, months=sign * n)
    if unit in ("year", "years"):
        return _apply_offset(ref_date, years=sign * n)

    return None


def main() -> None:
    print("Hello from nldate!")
