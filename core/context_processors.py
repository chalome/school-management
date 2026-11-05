from .school_years import school_year_context


def school_years(request):
    return school_year_context(request)
