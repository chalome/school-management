from .models import SchoolYear, active_school_year


SESSION_KEY = 'school_year_id'


def get_selected_school_year(request, active_year=None):
    active_year = active_year or active_school_year()
    selected_id = request.session.get(SESSION_KEY)
    if isinstance(selected_id, int) or (
        isinstance(selected_id, str) and selected_id.isdecimal()
    ):
        selected_year = SchoolYear.objects.filter(pk=selected_id).first()
        if selected_year:
            return selected_year
    request.session[SESSION_KEY] = active_year.pk
    return active_year


def school_year_context(request):
    active_year = active_school_year()
    return {
        'school_years': SchoolYear.objects.all(),
        'active_school_year': active_year,
        'selected_school_year': get_selected_school_year(request, active_year),
    }
