from django.test import TestCase

from .models import Exercise
from .models import Licence


class WorkoutsTestCase(TestCase):
    def test_create_exercise(self):
        licence = Licence(
            name="no licence",
            notice="licence free",
            link="http://example.com",
        )
        licence.save()

        exercise = Exercise(
            name="Run",
            description="Put one foot in front of the other, quickly.",
            source="http://example.com",
        )
        exercise.licence = licence
        exercise.save()

        self.assertEqual(Exercise.objects.filter(name="Run").get(), exercise)
