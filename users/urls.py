from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("api/friends/", views.FriendListView.as_view(), name="friends"),
    path("api/makefriends/", views.MakeNewFriendsView.as_view(), name="makefriends"),
    path(
        "api/friend/<int:friend>/", views.FriendCreateView.as_view(), name="makefriend"
    ),
]
