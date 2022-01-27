import datetime
import itertools
import random

from django.core.management.base import BaseCommand, CommandError
from users.models import User, Friend

# A list of colours that are used to generate usernames.
COLOURS = [
    "Aquamarine",
    "Chocolate",
    "Crimson",
    "Coral",
    "Magenta",
    "Olive",
    "Orchid",
    "Salmon",
    "Fire",
    "Ghost",
    "Golden",
    "Honey",
    "Lavender",
    "Lime",
    "Spring",
    "Rose",
    "Violet",
    "Peach",
    "Turquoise",
]

# A list of animals that are used to generate usernames.
ANIMALS = [
    "Aardvark",
    "Albatross",
    "Goat",
    "Alsatian",
    "Leopard",
    "Angelfish",
    "Antelope",
    "Fox",
    "Armadillo",
    "Alpaca",
    "Baboon",
    "Bandicoot",
    "Badger",
    "Barracuda",
    "Bison",
    "Camel",
    "Chinchilla",
    "Cockatoo",
    "Dingo",
    "Shrew",
    "Eskipoo",
    "Ermine",
]

FAKE_DOMAIN = "example.com"

usernames = list(itertools.product(set(COLOURS), set(ANIMALS)))
random.shuffle(usernames)
emails = [f"{c}{a}@{FAKE_DOMAIN}" for c, a in usernames]


def random_timestamp(dt):
    """Return a random datetime on the same day as `dt`. `dt` is assumed
    to be a ``datetime.datetime``."""
    start = dt.replace(hour=23, minute=59, second=59)
    end = dt.replace(hour=0, minute=0, second=0)
    max_timestamp = int(start.timestamp())
    min_timestamp = int(end.timestamp())

    timestamp = random.randrange(min_timestamp, max_timestamp)
    return datetime.datetime.fromtimestamp(timestamp)


class Command(BaseCommand):
    help = "Generate users with friends"

    def _delete(self):
        generated_users = User.objects.filter(email__in=emails)
        self.stdout.write(self.style.NOTICE(f"deleting {len(generated_users)}!"))
        generated_users.delete()

    def _create(self):
        users = []
        for names, email in zip(usernames, emails):
            nickname = "".join(names)
            self.stdout.write(self.style.SUCCESS(f"generating user {nickname}"))
            email = nickname + "@example.com"
            user = User(email=email, username=nickname)
            user.set_password(nickname)
            user.first_name = names[0]
            user.last_name = names[1]
            users.append(user)

        User.objects.bulk_create(users)
        self._friends()

    def _friends(self):
        users = list(User.objects.filter(email__in=emails))
        for user in users:
            friends = random.sample(users, random.randint(0, 12))

            for friend in friends:
                if user == friend:
                    continue
                self.stdout.write(
                    self.style.WARNING(
                        f"{user.username} and {friend.username} are friends"
                    )
                )

                Friend.objects.get_or_create(user=user, friend=friend)
                Friend.objects.get_or_create(user=friend, friend=user)

    def handle(self, *args, **options):
        self._delete()
        self._create()
