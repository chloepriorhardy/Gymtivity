from django.http import JsonResponse

from project.db.models import SerializableModel


class JSONResponseMixin:
    """A mixin that can be used to render a JSON response."""

    def render_to_json_response(self, context, **response_kwargs):
        """Returns a JSON response, transforming 'context' to make the payload."""
        return JsonResponse(
            self.get_data(context),
            json_dumps_params={"indent": 2},
            **response_kwargs,
        )

    def get_data(self, context):
        """Returns an object that will be serialized as JSON by json.dumps()."""
        context_object_name = getattr(self, "context_object_name")
        context_object = context.get(context_object_name)

        if isinstance(context_object, SerializableModel):
            data = context_object.serialize()
        else:
            data = [obj.serialize() for obj in context_object]

        # TODO: Add status code
        return {"data": {context_object_name: data}}
