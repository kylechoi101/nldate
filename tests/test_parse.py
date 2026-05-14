from datetime import date

from nldate import parse


class TestAbsoluteDates:
    def test_full_month_d_name_year(self):
        assert parse("December 1st, 2025") == date(2025, 12, 1)

    def test_abbreviated_month(self):
        assert parse("Dec 1, 2025") == date(2025, 12, 1)

    def test_ordinal_day(self):
        assert parse("January 3rd, 2024") == date(2024, 1, 3)
        assert parse("January 2nd, 2024") == date(2024, 1, 2)
        assert parse("January 21st, 2024") == date(2024, 1, 21)
        assert parse("January 22nd, 2024") == date(2024, 1, 22)
        assert parse("January 23rd, 2024") == date(2024, 1, 23)

    def test_iso_format(self):
        assert parse("2025-12-01") == date(2025, 12, 1)

    def test_us_slash_format(self):
        assert parse("12/01/2025") == date(2025, 12, 1)

    def test_us_dash_format(self):
        assert parse("12-01-2025") == date(2025, 12, 1)

    def test_dotted_format(self):
        assert parse("12.01.2025") == date(2025, 12, 1)

    def test_no_comma(self):
        assert parse("December 1 2025") == date(2025, 12, 1)


class TestRelativeToToday:
    def test_today(self):
        assert parse("today", date(2025, 6, 1)) == date(2025, 6, 1)

    def test_tomorrow(self):
        assert parse("tomorrow", date(2025, 6, 1)) == date(2025, 6, 2)

    def test_yesterday(self):
        assert parse("yesterday", date(2025, 6, 1)) == date(2025, 5, 31)

    def test_in_n_days(self):
        assert parse("in 3 days", date(2025, 6, 1)) == date(2025, 6, 4)

    def test_in_n_weeks(self):
        assert parse("in 2 weeks", date(2025, 6, 1)) == date(2025, 6, 15)

    def test_in_n_months(self):
        assert parse("in 1 month", date(2025, 6, 1)) == date(2025, 7, 1)

    def test_in_n_years(self):
        assert parse("in 5 years", date(2025, 6, 1)) == date(2030, 6, 1)

    def test_n_days_from_now(self):
        assert parse("3 days from now", date(2025, 6, 1)) == date(2025, 6, 4)

    def test_n_days_ago(self):
        assert parse("3 days ago", date(2025, 6, 5)) == date(2025, 6, 2)

    def test_singular_unit(self):
        assert parse("in 1 day", date(2025, 6, 1)) == date(2025, 6, 2)
        assert parse("in 1 week", date(2025, 6, 1)) == date(2025, 6, 8)

    def test_next_weekday(self):
        assert parse("next Tuesday", date(2025, 6, 1)) == date(2025, 6, 3)
        assert parse("next Monday", date(2025, 6, 1)) == date(2025, 6, 2)

    def test_last_weekday(self):
        assert parse("last Monday", date(2025, 6, 4)) == date(2025, 6, 2)
        assert parse("last Friday", date(2025, 6, 4)) == date(2025, 5, 30)

    def test_this_weekday(self):
        assert parse("this Tuesday", date(2025, 6, 1)) == date(2025, 6, 3)

    def test_weekday_past_or_future(self):
        assert parse("Tuesday", date(2025, 6, 3)) == date(2025, 6, 3)
        assert parse("Tuesday", date(2025, 6, 1)) == date(2025, 6, 3)

    def test_next_week_default_today(self):
        result = parse("tomorrow")
        from datetime import date as d

        assert isinstance(result, d)


class TestRelativeToDate:
    def test_before_absolute(self):
        assert (
            parse("5 days before December 1st, 2025")
            == date(2025, 11, 26)
        )

    def test_after_absolute(self):
        assert (
            parse("5 days after December 1st, 2025")
            == date(2025, 12, 6)
        )

    def test_months_before(self):
        assert (
            parse("2 months before December 1st, 2025")
            == date(2025, 10, 1)
        )

    def test_years_after(self):
        assert (
            parse("1 year after December 1st, 2025")
            == date(2026, 12, 1)
        )

    def test_weeks_before(self):
        assert (
            parse("2 weeks before December 1st, 2025")
            == date(2025, 11, 17)
        )

    def test_relative_to_yesterday(self):
        assert (
            parse("3 days after yesterday", date(2025, 6, 10))
            == date(2025, 6, 12)
        )

    def test_relative_to_tomorrow(self):
        assert (
            parse("5 days before tomorrow", date(2025, 6, 10))
            == date(2025, 6, 6)
        )

    def test_relative_to_today(self):
        assert (
            parse("1 week before today", date(2025, 6, 10))
            == date(2025, 6, 3)
        )


class TestCompoundRelative:
    def test_years_and_months_after(self):
        assert (
            parse("1 year and 2 months after yesterday", date(2025, 6, 1))
            == date(2026, 7, 31)
        )

    def test_years_months_days_before(self):
        assert (
            parse("1 year 2 months 3 days before 2025-01-01")
            == date(2023, 10, 29)
        )

    def test_weeks_and_days_after(self):
        assert (
            parse("2 weeks and 3 days after January 1st, 2025")
            == date(2025, 1, 18)
        )


class TestWeekdays:
    def test_next_wednesday(self):
        assert parse("next Wednesday", date(2025, 6, 1)) == date(2025, 6, 4)

    def test_last_sunday(self):
        assert parse("last Sunday", date(2025, 6, 4)) == date(2025, 6, 1)

    def test_this_saturday(self):
        assert parse("this Saturday", date(2025, 6, 2)) == date(2025, 6, 7)

    def test_next_friday_before_today_after_weekend(self):
        assert parse("next Friday", date(2025, 6, 5)) == date(2025, 6, 6)
        assert parse("next Friday", date(2025, 6, 7)) == date(2025, 6, 13)

    def test_weekday_relative_with_default_today(self):
        result = parse("next Monday")
        from datetime import date as d

        assert isinstance(result, d)


class TestEdgeCases:
    def test_ordinal_numbers_in_between(self):
        assert (
            parse("5th day after January 1st, 2025")
            == date(2025, 1, 6)
        )

    def test_no_space_after_comma(self):
        assert parse("December 1st,2025") == date(2025, 12, 1)

    def test_lowercase_month(self):
        assert parse("december 1st, 2025") == date(2025, 12, 1)

    def test_lowercase_relative(self):
        assert parse("in 3 days", date(2025, 6, 1)) == date(2025, 6, 4)

    def test_end_of_month(self):
        assert parse("January 31st, 2025") == date(2025, 1, 31)

    def test_leap_year(self):
        assert parse("February 29th, 2024") == date(2024, 2, 29)

    def test_midnight_does_not_matter(self):
        assert parse("today", date(2025, 1, 1)) == date(2025, 1, 1)


class TestNoTodayParam:
    def test_defaults_to_today(self):
        result = parse("today")
        from datetime import date as d

        assert isinstance(result, d)
