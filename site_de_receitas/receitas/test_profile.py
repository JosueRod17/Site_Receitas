from django.contrib.auth.models import User
from django.test import TestCase

from .forms import ProfileForm


class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ana@example.com",
            email="ana@example.com",
            first_name="Ana",
            password="senha-segura-123",
        )

    def form_data(self, **overrides):
        data = {
            "nickname": "Ana",
            "email": "ana@example.com",
            "current_password": "",
            "new_password1": "",
            "new_password2": "",
        }
        data.update(overrides)
        return data

    def test_shows_current_email_as_initial_value(self):
        form = ProfileForm(self.user)

        self.assertEqual(form["email"].value(), "ana@example.com")

    def test_saves_new_email_and_updates_matching_username(self):
        form = ProfileForm(
            self.user,
            self.form_data(
                nickname="Ana Silva",
                email="ana.silva@example.com",
                current_password="senha-segura-123",
            ),
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.first_name, "Ana Silva")
        self.assertEqual(user.email, "ana.silva@example.com")
        self.assertEqual(user.username, "ana.silva@example.com")

    def test_keeps_an_independent_username_when_email_changes(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="senha-segura-123",
        )
        form = ProfileForm(
            admin,
            self.form_data(
                nickname="Admin",
                email="novo-admin@example.com",
                current_password="senha-segura-123",
            ),
        )

        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "novo-admin@example.com")

    def test_rejects_email_already_used_by_another_account(self):
        User.objects.create_user(
            username="bia@example.com",
            email="bia@example.com",
            password="senha-segura-123",
        )
        form = ProfileForm(self.user, self.form_data(email="BIA@EXAMPLE.COM"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_requires_current_password_to_change_email(self):
        form = ProfileForm(
            self.user,
            self.form_data(email="novo-email@example.com"),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("current_password", form.errors)

    def test_allows_nickname_change_without_current_password(self):
        form = ProfileForm(self.user, self.form_data(nickname="Ana Maria"))

        self.assertTrue(form.is_valid())

    def test_rejects_email_that_is_another_users_username(self):
        User.objects.create_user(
            username="reservado@example.com",
            email="outro@example.com",
            password="senha-segura-123",
        )
        form = ProfileForm(self.user, self.form_data(email="reservado@example.com"))

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_validates_new_password_against_new_email_and_nickname(self):
        form = ProfileForm(
            self.user,
            self.form_data(
                nickname="Ana Cozinha",
                email="cozinha@example.com",
                current_password="senha-segura-123",
                new_password1="cozinha@example.com",
                new_password2="cozinha@example.com",
            ),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("new_password1", form.errors)
