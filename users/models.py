from django.core.serializers import serialize
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

from project.db.models import SerializableModel


class CustomUserManager(UserManager):
    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        if not username:
            username = email
        else:
            username = User.normalize_username(username)

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"),
        blank=False,
        unique=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # For createsuperuser only.

    def serialize(self, format="python"):
        obj = serialize(format, [self])[0]["fields"]
        obj["id"] = self.pk
        del obj["password"]
        del obj["groups"]
        del obj["user_permissions"]
        del obj["is_superuser"]
        return obj


class Friend(SerializableModel):
    """The friend model.

    An edge list for users in our friends network.
    """

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="+",
    )

    friend = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="friend+",
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"

    def serialize(self, format="python"):
        obj = super().serialize(format)
        obj["friend"] = self.friend.serialize(format)
        return obj
