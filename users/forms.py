from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from .models import User
 
 
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

 
class CustomUserChangeFrom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User