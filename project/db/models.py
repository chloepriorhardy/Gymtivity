from django.core.serializers import serialize
from django.db.models import Model


class SerializableModel(Model):
    class Meta:
        abstract = True

    def serialize(self, format="python"):
        obj = serialize(format, [self])[0]["fields"]
        obj["id"] = self.pk
        return obj
