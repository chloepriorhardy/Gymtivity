from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import Exercise
from .models import Licence


class WorkoutsTestCase(TestCase):
    fixtures = ["workouts.json"]

    def login(self):
        email, password = "testuser@example.com", "Passw0rd!!"
        user = User.objects.create_user(email=email, password=password)
        self.client.login(username=email, password=password)
        return user

    def test_create_exercise(self):
        licence = Licence(
            name="no licence",
            notice="licence free",
            link="http://example.com",
        )
        licence.save()

        exercise = Exercise(
            name="A Run",
            description="Put one foot in front of the other, quickly.",
            source="http://example.com",
        )
        exercise.licence = licence
        exercise.save()

        self.assertEqual(Exercise.objects.filter(name="A Run").get(), exercise)

    def test_get_workout(self):
        """Test that we can get workout data using the AJAX API."""
        self.login()
        response = self.client.get(reverse("workouts:workouts"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_workouts_requires_login(self):
        """Test the workout AJAX API requires a login."""
        response = self.client.get(reverse("workouts:workouts"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
