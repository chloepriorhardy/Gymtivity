from django.views.generic.edit import FormView
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.http import HttpResponseRedirect
 
from .forms import CustomUserCreationForm
 
 
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