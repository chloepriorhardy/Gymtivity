import json
import logging
import sys
import traceback

from functools import wraps
from http import HTTPStatus

from django.conf import settings

from django.http import Http404
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse

from django.utils.translation import gettext as _


logger = logging.getLogger("django.request")


def ajax_required(func):
    """A view decorator that returns an HttpResponseBadRequest if the request is not AJAX"""

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("expected and XMLHttpRequest")
        return func(request, *args, **kwargs)

    return wrapper


def json_required(func):
    """A view decorator that returns an HttpResponseBadRequest if the request body is not valid
    JSON.

    If JSON decoding is successful, request data is stored as `request.data`.
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            request.data = json.load(request)
        except json.JSONDecodeError as err:
            return HttpResponseBadRequest(str(err))
        return func(request, *args, **kwargs)

    return wrapper


def extract_traceback(ex):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(
        traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])
    )
    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]
    return exception_str


def json_view(func):
    """A view decorator that returns a JsonResponse."""

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        resp = {"status": HTTPStatus.OK, "message": None, "data": {}}

        try:
            response = func(request, *args, **kwargs)
            if isinstance(response, HttpResponseNotAllowed):
                resp["status"] = HTTPStatus.METHOD_NOT_ALLOWED
                resp["message"] = HTTPStatus.METHOD_NOT_ALLOWED.name
            else:
                obj, status = response
                resp["status"] = status
                resp["data"] = obj
        except Http404 as err:
            resp["status"] = HTTPStatus.NOT_FOUND
            resp["message"] = str(err)
        except Exception as err:
            resp["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            if settings.DEBUG:
                resp["message"] = str(err)
            else:
                resp["message"] = _("unexpected server error")

            logger.error(
                "Internal server error: %s\n%s",
                request.path,
                extract_traceback(err),
            )
        return JsonResponse(resp, status=resp["status"])

    return wrapper
