from django.conf import settings
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django.views.generic import View
from django.views.generic.edit import FormView
from django.views.generic.list import BaseListView


from project.views.generic import JSONResponseMixin

from .forms import CustomUserCreationForm
from .models import Friend
from .models import User

from .core import get_friends


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = settings.LOGIN_REDIRECT_URL

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.username = new_user.email
        new_user.save()

        username = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class FriendListView(JSONResponseMixin, LoginRequiredMixin, View):
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return self.render_to_json_response({})

    def get_data(self, context):
        return {"data": get_friends(self.request.user.id)}


class FriendCreateView(JSONResponseMixin, LoginRequiredMixin, View):
    context_object_name = "friend"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        friends, created = Friend.objects.get_or_create(
            user=self.request.user,
            friend=User.objects.get(pk=self.kwargs["friend"]),
        )

        reverse_friend, created = Friend.objects.get_or_create(
            user=User.objects.get(pk=self.kwargs["friend"]),
            friend=self.request.user,
        )

        return self.render_to_json_response({self.context_object_name: friends})

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)
