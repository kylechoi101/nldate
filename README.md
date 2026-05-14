# nldate

A natural-language date parser. Converts date strings like "5 days before December 1st, 2025" or "next Tuesday" into `datetime.date` objects.

## Usage

```python
from nldate import parse
from datetime import date

parse("December 1st, 2025")                     # date(2025, 12, 1)
parse("next Tuesday", today=date(2025, 6, 1))   # date(2025, 6, 3)
parse("5 days before December 1st, 2025")       # date(2025, 11, 26)
parse("1 year and 2 months after yesterday",
      today=date(2025, 6, 1))                   # date(2026, 7, 31)
```
