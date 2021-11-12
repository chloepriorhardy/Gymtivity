from datetime import timedelta

from django.core.serializers import serialize
from django.conf import settings
from django.core import validators
from django.db import models
from django.db import connection
from django.utils.functional import cached_property

import humanize

from project.db.models import SerializableModel


class Workout(SerializableModel):
    """The workout model.

    A workout is a collection of one or more schemes. A workout can be completed zero or
    more times by zero or more users. A completed workout is recorded as a `Session`.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A name for the workout.",
    )

    description = models.TextField(help_text="Describe the workout.")

    rounds = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(1000),
        ],
        help_text="The number of times each scheme is to be performed during this workout.",
    )

    time_limit = models.DurationField(
        blank=True,
        default=timedelta,
        help_text="An optional time limit for the workout.",
    )

    @cached_property
    def exercise_count(self):
        """Return the number of distinct exercises in this workout."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(DISTINCT exercise_id) "
                "FROM workouts_workout "
                "JOIN workouts_interval "
                "ON workouts_workout.id = workouts_interval.workout_id "
                "JOIN workouts_scheme "
                "ON workouts_interval.id = workouts_scheme.interval_id "
                "WHERE workouts_workout.id = %s;",
                [self.pk],
            )
            row = cursor.fetchone()
        return row[0]

    @cached_property
    def style(self):
        return self.interval_set.first().style

    def __str__(self):
        return str(self.name)

    def serialize(self, format="python"):
        obj = super().serialize(format)
        obj["exercise_count"] = self.exercise_count
        obj["intervals"] = [
            interval.serialize(format) for interval in self.interval_set.all()
        ]
        return obj


class Session(SerializableModel):
    """The session model.

    A session is a record of a single user completing single workout at a specific time, with
    performance information per `Scheme` in the `Workout`.
    """

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="The user that completed the workout.",
    )

    workout = models.ForeignKey(
        to=Workout,
        on_delete=models.CASCADE,
        help_text="The workout complete during this session.",
    )

    timestamp = models.DateTimeField(
        help_text="Date and time the workout was completed."
    )

    @cached_property
    def performance(self):
        """Return the performance measure for each interval in this session."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT performance, quantity_name "
                "FROM workouts_performance "
                "JOIN workouts_interval "
                "ON workouts_performance.interval_id = workouts_interval.id "
                "JOIN workouts_workoutstyle "
                "ON workouts_interval.style_id = workouts_workoutstyle.id "
                "WHERE workouts_performance.session_id = %s",
                [self.pk],
            )
            row = cursor.fetchone()

        performance = row[0]
        quantity_name = WorkoutStyle.QuantityNameChoices(row[1]).label

        # TODO: Humanize performance
        if quantity_name == "Time":
            performance = humanize.naturaldelta(
                performance, minimum_unit="milliseconds"
            )

        return {"performance": performance, "quantity_name": quantity_name}

    def serialize(self, format="python"):
        obj = serialize(format, [self])[0]["fields"]
        obj["id"] = self.pk
        obj["user"] = self.user.serialize()
        obj["workout"] = self.workout.serialize()
        obj["performance"] = self.performance
        return obj


class WorkoutStyle(SerializableModel):
    """The workout style model.

    A workout style describes the objective or measure of performance of an exercise block.
    """

    name = models.CharField(
        max_length=255, help_text="A name for the style of workout. E.g. AMRAP."
    )
    description = models.TextField(
        help_text="A longer description of this style of workout."
    )

    class QuantityNameChoices(models.TextChoices):
        TIME = "T", "Time"
        DISTANCE = "D", "Distance"
        WEIGHT = "W", "Weight"
        REPS = "R", "Repetitions"
        ROW = "A", "Rate of work"

    quantity_name = models.CharField(
        max_length=255,
        choices=QuantityNameChoices.choices,
        default=QuantityNameChoices.TIME,
        help_text="Name of the physical quantity that measures this style of workout.",
    )

    def __str__(self):
        return str(self.name)


class Interval(SerializableModel):
    """The workout interval model.

    A workout interval is a collection of one or more exercise schemes with an associated workout
    style. One or more intervals make up a `Workout`.

    When doing an exercise for reps, you might call an interval a "set" or "super set" if each
    interval include more than one exercise.
    """

    workout = models.ForeignKey(
        to=Workout,
        on_delete=models.CASCADE,
    )

    repeat = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(1000),
        ],
        help_text="The number of times each exercise scheme is to be performed.",
    )

    time_limit = models.DurationField(
        blank=True,
        default=timedelta,
        help_text="An optional time limit for the exercise.",
    )

    style = models.ForeignKey(
        to=WorkoutStyle,
        on_delete=models.CASCADE,
        help_text="The objective or measure of performance for this exercise interval.",
    )

    rest = models.DurationField(
        blank=True,
        default=timedelta,
        help_text="Optional post-interval rest period.",
    )

    # TODO: Add sequence field

    def __str__(self):
        exercises = self.scheme_set.all()
        exercise_count = len(exercises)

        if exercise_count == 1:
            return f"{exercises[0]} - {self.style}"
        return f"{exercises[0]} + {exercise_count - 1} - {self.style}"

    def serialize(self, format="python"):
        obj = super().serialize(format)
        obj["schemes"] = [scheme.serialize(format) for scheme in self.scheme_set.all()]
        obj["style"] = self.style.serialize(format)
        return obj


class Scheme(SerializableModel):
    """The scheme model.

    An exercise scheme defines a target number of reps, calories, distance or time limit for a
    specific exercise. One or more exercise schemes make up a workout interval.
    """

    interval = models.ForeignKey(to=Interval, on_delete=models.CASCADE)
    exercise = models.ForeignKey(to="Exercise", on_delete=models.CASCADE)

    reps = models.PositiveSmallIntegerField(
        blank=True,
        default=0,
        help_text="Optional number of reps to complete for this exercise.",
    )

    duration = models.DurationField(
        blank=True,
        default=timedelta,
        help_text="Optional duration of the exercise.",
    )

    distance = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Optional target distance for the exercise in meters.",
    )

    time_limit = models.DurationField(
        blank=True,
        default=timedelta,
        help_text="An optional time limit for the exercise.",
    )

    calories = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Target calorie count for the exercise.",
    )

    pace_one = models.DurationField(editable=False, blank=True, default=timedelta)
    pace_two = models.DurationField(editable=False, blank=True, default=timedelta)
    pace_three = models.DurationField(editable=False, blank=True, default=timedelta)

    def __str__(self):
        if self.reps:
            return f"{self.exercise} x {self.reps}"
        if self.time_limit:
            return f"{self.exercise} for {self.time_limit}"
        if self.calories:
            return f"{self.exercise} for {self.calories}"
        if self.distance:
            return f"{self.distance}m {self.exercise}"
        return f"{self.exercise} for {self.scheme.time_limit}"

    def serialize(self, format="python"):
        obj = super().serialize(format=format)
        obj["exercise"] = self.exercise.serialize(format)
        # XXX: I can't remember what I was thinking with these.
        del obj["pace_one"]
        del obj["pace_two"]
        del obj["pace_three"]
        return obj


class Licence(SerializableModel):
    """Exercise licence attribution.

    Many exercise descriptions were initially taken from Wikipedia, released under the Creative
    Commons Attribution-ShareAlike Licence. This, and potentially other workout description sources
    require attribution.
    """

    name = models.CharField(max_length=255, help_text="Name of the licence.")

    notice = models.TextField(
        blank=True,
        default="",
        help_text="An optional notice do display with content covered by this licence.",
    )

    link = models.URLField(help_text="A link to the full licence terms.")

    def __str__(self):
        return str(self.name)


class Exercise(SerializableModel):
    """The exercise model.

    An exercises, along with an exercise scheme (reps, sets, time limit, etc.), are combined
    into a `Workout` that a user can complete in a `Session`.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the exercise.",
    )

    description = models.TextField(
        help_text=(
            "A long description of the exercise. Including a description of the proper "
            "form and any required equipment."
        )
    )

    source = models.URLField(
        blank=True,
        default="",
        help_text="A link to the source material.",
    )

    licence = models.ForeignKey(
        to=Licence,
        on_delete=models.CASCADE,
        help_text="The licence this exercise content is covered by.",
    )

    def __str__(self):
        return str(self.name)


NormFeatureValidators = [
    validators.MinValueValidator(0),
    validators.MaxValueValidator(1),
]


class MuscleGroupFeatures(SerializableModel):
    """The muscle group model.

    Every exercise works one or more muscles or muscle groups. Some muscle groups are the primary
    target of an exercise, represented with values close to 1. Others are secondary or only
    activated in a minor way, represented with values closer to 0.
    """

    exercise = models.OneToOneField(
        to=Exercise,
        on_delete=models.CASCADE,
    )

    calves = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target calves?",
    )

    quads = models.DecimalField(
        verbose_name="Quadricepts",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the quadricepts?",
    )

    hamstrings = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the hamstrings?",
    )

    gluteus = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the gluteus?",
    )

    Hips = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the hips?",
    )

    lower_back = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the lower back?",
    )

    lats = models.DecimalField(
        verbose_name="Latissimus dorsi",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the lats?",
    )

    traps = models.DecimalField(
        verbose_name="Trapezius",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the traps?",
    )

    abs = models.DecimalField(
        verbose_name="Abdominals",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the abs?",
    )

    pecs = models.DecimalField(
        verbose_name="Pectorals",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the pecs?",
    )

    delts = models.DecimalField(
        verbose_name="Deltoids",
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the delts?",
    )

    triceps = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the triceps?",
    )

    biceps = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the biceps?",
    )

    forearms = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=NormFeatureValidators,
        help_text="How much does the exercise target the forearms?",
    )

    def __str__(self):
        return str(self.exercise)


class Performance(SerializableModel):
    """The workout performance model.

    One user can record performance for one or more workout interval per workout session.
    """

    session = models.ForeignKey(to=Session, on_delete=models.CASCADE)
    interval = models.ForeignKey(to=Interval, on_delete=models.CASCADE)
    performance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="A measure of performance. Performance units depend on the style of the workout.",
    )


class Like(SerializableModel):
    """The likes model.

    This is a history of explicit like and/or dislike user actions for workouts.
    """

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout = models.ForeignKey(to=Workout, on_delete=models.CASCADE)

    # False for an un-like, thumbs down or un-pin action, True for like, thumbsup or pin.
    action = models.BooleanField()
    timestamp = models.DateTimeField()
