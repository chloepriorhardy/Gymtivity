from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from .models import Friend

from .forms import CustomUserChangeFrom
from .forms import CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeFrom
    add_form = CustomUserCreationForm
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)


class FriendAdmin(admin.ModelAdmin):
    pass


admin.site.register(Friend, FriendAdmin)
