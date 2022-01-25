from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from workouts.models import Session


@login_required
def index(request):
    # TODO: Filter on user and friends
    # TODO: Pagination
    sessions = (
        Session.objects.all().select_related("workout").order_by("-timestamp")[:10]
    )

    context = {
        "sessions": sessions,
    }

    return render(request, "dashboard/dashboard.html", context=context)
