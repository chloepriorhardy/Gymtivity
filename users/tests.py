from http import HTTPStatus
from urllib.parse import urlencode

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .models import User
from .core import _add_friend
from .core import _find_new_friends


class LoginTestCase(TestCase):
    def test_login_redirect(self):
        """Test that we get redirected to the login page."""
        url = reverse("index")
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            f"{reverse('login')}?{urlencode({'next': url})}",
        )

    def test_login(self):
        """Test that a user can log in."""
        email, password = "testuser@example.com", "Passw0rd!!"
        User.objects.create_user(email=email, password=password)
        self.assertTrue(self.client.login(username=email, password=password))

    def test_failed_login(self):
        """Test that non-existent users can not log in."""
        email, password = "nosuchuser", "secret"
        self.assertFalse(self.client.login(username=email, password=password))

    def test_login_form(self):
        """Test that a user can log in using the login form."""
        email, password = "testuser@example.com", "Passw0rd!!"
        User.objects.create_user(email=email, password=password)

        response = self.client.post(
            reverse("login"), {"username": email, "password": password}
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_failed_login_form(self):
        """Test that users can't log in with incorrect credentials."""
        email, password = "nosuchuser", "secret"
        response = self.client.post(
            reverse("login"), {"username": email, "password": password}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # XXX: This text will probably change.
        self.assertContains(
            response, "Please enter a correct email address and password."
        )


class RegistrationTestCase(TestCase):
    def test_registration_form(self):
        """Test that we can register a new user."""
        email, password = "testuser@example.com", "Passw0rd!!"

        response = self.client.post(
            reverse("users:register"),
            {"email": email, "password1": password, "password2": password},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(self.client.login(username=email, password=password))

    def test_subsequent_registration(self):
        """Test that multiple users can register.

        This test covers an error condition we had where only the first
        registered user would succeed due to a database constraint violation.
        """
        credentials = [
            ("testuser@example.com", "Passw0rd!!"),
            ("hello@example.com", "Passw0rd£$"),
        ]

        for email, password in credentials:
            response = self.client.post(
                reverse("users:register"),
                {"email": email, "password1": password, "password2": password},
            )

            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertTrue(self.client.login(username=email, password=password))


class TestGraph(TestCase):
    def test_make_graph(self):
        """Test that we can build a graph implemented as an adjacency list."""
        users = [f"User{i}" for i in range(10)]
        friends = [
            (users[0], users[2]),
            (users[0], users[3]),
            (users[2], users[5]),
        ]

        graph = {}
        for user, friend in friends:
            _add_friend(graph, user, friend)

        self.assertIn(users[2], graph[users[0]])
        self.assertIn(users[0], graph[users[2]])
        self.assertIn(users[3], graph[users[0]])
        self.assertIn(users[5], graph[users[2]])
        self.assertNotIn(users[0], graph[users[5]])

    def test_find_friends(self):
        users = [f"User{i}" for i in range(10)]
        friends = [
            (users[0], users[2]),
            (users[0], users[3]),
            (users[2], users[5]),
        ]

        graph = {}
        for user, friend in friends:
            _add_friend(graph, user, friend)

        potential_friends = _find_new_friends(graph, users[2])

        self.assertEqual(len(potential_friends), 1)
        self.assertIn(users[3], potential_friends)
        self.assertNotIn(users[2], potential_friends)
        self.assertNotIn(users[5], potential_friends)
        self.assertNotIn(users[6], potential_friends)
