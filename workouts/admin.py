from django.contrib import admin

import nested_admin


from .models import Session
from .models import Workout
from .models import WorkoutStyle
from .models import Interval
from .models import Exercise
from .models import Scheme
from .models import Licence
from .models import MuscleGroupFeatures
from .models import Performance


class PerformanceInline(admin.TabularInline):
    model = Performance
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "interval":
            if request.workout_session:
                kwargs["queryset"] = Interval.objects.filter(
                    workout=request.workout_session.workout
                )
            else:
                kwargs["queryset"] = Interval.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SessionAdmin(admin.ModelAdmin):
    list_display = ["get_session_description", "user", "workout", "timestamp"]
    inlines = [PerformanceInline]
    autocomplete_fields = ["workout", "user"]

    def get_form(self, request, obj=None, **kwargs):
        # Save the current session object on the request for the benefit of PerformanceInline.
        request.workout_session = obj
        return super().get_form(request, obj, **kwargs)

    @admin.display(description="Session")
    def get_session_description(self, obj):
        return f"{obj.workout} at {obj.timestamp}"


admin.site.register(Session, SessionAdmin)


class WorkoutStyleAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


admin.site.register(WorkoutStyle, WorkoutStyleAdmin)


class MuscleGroupFeaturesInline(admin.StackedInline):
    model = MuscleGroupFeatures


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "source", "get_licence"]
    inlines = [MuscleGroupFeaturesInline]

    @admin.display(description="Licence")
    def get_licence(self, obj):
        return obj.licence.name


admin.site.register(Exercise, ExerciseAdmin)


class LicenceAdmin(admin.ModelAdmin):
    list_display = ["name", "link"]


admin.site.register(Licence, LicenceAdmin)


class SchemeInline(nested_admin.NestedTabularInline):
    model = Scheme
    extra = 1


class IntervalInline(nested_admin.NestedStackedInline):
    model = Interval
    extra = 0
    inlines = [SchemeInline]
    inline_classes = (
        "collapse",
        "open",
        "grp-collapse",
        "grp-open",
    )


class WorkoutAdmin(nested_admin.NestedModelAdmin):
    model = Workout
    list_display = ["name", "get_style", "rounds", "time_limit"]
    search_fields = ["name", "description"]
    inlines = [IntervalInline]

    @admin.display(description="Style")
    def get_style(self, obj):
        styles = [str(block.style) for block in obj.interval_set.all()]
        return ", ".join(set(styles))


admin.site.register(Workout, WorkoutAdmin)
