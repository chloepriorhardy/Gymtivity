from http import HTTPStatus
 
from django.test import SimpleTestCase
from django.urls import reverse
 
 
class LandingPageTestCase(SimpleTestCase):
   def test_landing_page_loads(self):
       """Test that the landing page loads."""
       response = self.client.get(reverse("landing:index"))
       self.assertEqual(response.status_code, HTTPStatus.OK)
 
   def test_landing_link_to_login(self):
       """Test that the landing page contains a link to the login page."""
       response = self.client.get(reverse("landing:index"))
       self.assertEqual(response.status_code, HTTPStatus.OK)
       self.assertContains(response, "Login")
 
   def test_landing_link_to_registration(self):
       """Test that the landing page contains a link to the sign up page."""
       response = self.client.get(reverse("landing:index"))
       self.assertEqual(response.status_code, HTTPStatus.OK)
       self.assertContains(response, "Sign Up")


