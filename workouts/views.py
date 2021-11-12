from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from project.views.generic import JSONResponseMixin

from workouts.models import Exercise
from workouts.models import Session
from workouts.models import Workout


class SessionDetailView(JSONResponseMixin, LoginRequiredMixin, BaseDetailView):
    context_object_name = "session"
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        # XXX: Not filtering by user during development.
        return Session.objects.select_related("workout")


class SessionListView(JSONResponseMixin, LoginRequiredMixin, BaseListView):
    context_object_name = "sessions"
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        # XXX: Not filtering by user during development.
        # TODO: Pagination
        return Session.objects.select_related("workout").order_by("-timestamp")


class WorkoutDetailView(JSONResponseMixin, LoginRequiredMixin, BaseDetailView):
    context_object_name = "workout"
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        # XXX: Not filtering by user during development.
        # TODO: Prefetch related
        return Workout.objects.all()


class WorkoutListView(JSONResponseMixin, LoginRequiredMixin, BaseListView):
    context_object_name = "workouts"
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        # XXX: Not filtering by user during development.
        # TODO: Pagination
        return Workout.objects.all()


class ExerciseDetailView(JSONResponseMixin, LoginRequiredMixin, BaseDetailView):
    context_object_name = "exercise"
    raise_exception = True
    model = Exercise

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class ExerciseListView(JSONResponseMixin, LoginRequiredMixin, BaseListView):
    context_object_name = "exercises"
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def get_queryset(self):
        # XXX: Not filtering by user during development.
        # TODO: Pagination
        return Exercise.objects.all()
