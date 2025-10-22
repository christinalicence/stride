from django.test import TestCase


# Create your tests here.

# Test setups

# Tests for models

# Tests for views

class TestUserProfileForm(TestCase):
    def test_form_is_valid(self):
        user_profile_form = UserProfileForm({'username': 'this is a name'})
        self.assertTrue(user_profile_form.is_valid)


# Tests that data is displayed correctly

# Security tests