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
    def save_model(self, request, obj, form, change) -> None:
        reverse_friend, created = Friend.objects.get_or_create(
            user=obj.friend,
            friend=obj.user,
            timestamp=obj.timestamp,
        )
        return super().save_model(request, obj, form, change)


admin.site.register(Friend, FriendAdmin)
