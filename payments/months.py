from datetime import date

from django.utils import timezone


MONTH_NAMES = (
    'Janvier',
    'Février',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Août',
    'Septembre',
    'Octobre',
    'Novembre',
    'Décembre',
)


def _month_from_value(value):
    try:
        year, month = value.split('-', 1)
        parsed_month = date(int(year), int(month), 1)
        if parsed_month.strftime('%Y-%m') == value:
            return parsed_month
    except (AttributeError, TypeError, ValueError):
        pass

    parts = value.rsplit(' ', 1)
    if len(parts) == 2:
        name, year = parts
        month_lookup = {item.casefold(): index for index, item in enumerate(MONTH_NAMES, 1)}
        try:
            month_number = month_lookup[name.casefold()]
            return date(int(year), month_number, 1)
        except (KeyError, ValueError):
            pass
    return None


def month_value(month_date):
    return month_date.strftime('%Y-%m')


def month_label(value):
    month_date = _month_from_value(value)
    if month_date is None:
        return value
    return f'{MONTH_NAMES[month_date.month - 1]} {month_date.year}'


def month_choices(existing_values=()):
    current = timezone.localdate().replace(day=1)
    start_index = current.year * 12 + current.month - 1 - 12
    choices_by_value = {}

    for offset in range(25):
        month_index = start_index + offset
        year, zero_based_month = divmod(month_index, 12)
        value = f'{year:04d}-{zero_based_month + 1:02d}'
        choices_by_value[value] = month_label(value)

    for value in existing_values:
        if value:
            choices_by_value.setdefault(value, month_label(value))

    return sorted(
        choices_by_value.items(),
        key=lambda choice: (
            _month_from_value(choice[0]) is None,
            _month_from_value(choice[0]) or date.min,
            choice[0],
        ),
        reverse=True,
    )


def school_year_month_choices(school_year, existing_values=()):
    start = school_year.start_date.replace(day=1)
    end = school_year.end_date.replace(day=1)
    choices_by_value = {}
    current = start
    while current <= end:
        value = month_value(current)
        choices_by_value[value] = month_label(value)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    for value in existing_values:
        if value:
            choices_by_value.setdefault(value, month_label(value))

    return sorted(
        choices_by_value.items(),
        key=lambda choice: (
            _month_from_value(choice[0]) is None,
            _month_from_value(choice[0]) or date.min,
            choice[0],
        ),
        reverse=True,
    )
