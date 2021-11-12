from django.urls import path

from . import views

app_name = "workouts"
urlpatterns = [
    path("session/<int:pk>/", views.SessionDetailView.as_view(), name="session"),
    path("sessions/", views.SessionListView.as_view(), name="sessions"),
    path("workout/<int:pk>/", views.WorkoutDetailView.as_view(), name="workout"),
    path("workouts/", views.WorkoutListView.as_view(), name="workouts"),
    path("exercise/<int:pk>/", views.ExerciseDetailView.as_view(), name="exercise"),
    path("exercises/", views.ExerciseListView.as_view(), name="exercises"),
]
