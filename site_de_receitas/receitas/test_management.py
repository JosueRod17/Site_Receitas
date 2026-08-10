from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Favorite, Membros, Recipe, Review


class ManagementAccessTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="senha-segura-123",
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="senha-segura-123",
        )

    def test_management_requires_a_superuser(self):
        response = self.client.get(reverse("management_dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('membros')}?auth=login",
            fetch_redirect_response=False,
        )

        self.client.force_login(self.member)
        response = self.client.get(reverse("management_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_legacy_member_mutation_is_not_public(self):
        response = self.client.get(reverse("criar_membro"))
        self.assertRedirects(
            response,
            f"{reverse('membros')}?auth=login",
            fetch_redirect_response=False,
        )


class ManagementCrudTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="senha-segura-123",
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="senha-segura-123",
        )
        self.client.force_login(self.superuser)

    def test_superuser_sees_dashboard_and_all_management_sections(self):
        section_urls = [
            "management_dashboard",
            "management_recipes",
            "management_reviews",
            "management_favorites",
            "management_members",
            "management_users",
            "management_groups",
        ]

        for url_name in section_urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Painel de gestão")

    def test_recipe_review_and_favorite_can_be_managed(self):
        response = self.client.post(
            reverse("management_recipe_create"),
            {
                "title": "Receita administrativa",
                "category": "Teste",
                "image_url": "https://example.com/recipe.jpg",
                "prep_time": 25,
                "difficulty": "Fácil",
                "description": "Descrição",
                "ingredients": "Ingrediente",
                "preparation": "Passo",
                "is_featured": "on",
            },
        )
        self.assertRedirects(response, reverse("management_recipes"))
        recipe = Recipe.objects.get(title="Receita administrativa")

        response = self.client.post(
            reverse("management_review_create"),
            {"recipe": recipe.pk, "user": self.member.pk, "rating": 5, "comment": "Ótima"},
        )
        self.assertRedirects(response, reverse("management_reviews"))
        review = Review.objects.get(recipe=recipe, user=self.member)

        response = self.client.post(
            reverse("management_favorite_create"),
            {"recipe": recipe.pk, "user": self.member.pk},
        )
        self.assertRedirects(response, reverse("management_favorites"))
        favorite = Favorite.objects.get(recipe=recipe, user=self.member)

        response = self.client.post(reverse("management_review_delete", args=[review.pk]))
        self.assertRedirects(response, reverse("management_reviews"))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

        response = self.client.post(reverse("management_favorite_delete", args=[favorite.pk]))
        self.assertRedirects(response, reverse("management_favorites"))
        self.assertFalse(Favorite.objects.filter(pk=favorite.pk).exists())

    def test_members_users_and_groups_can_be_managed(self):
        response = self.client.post(
            reverse("management_member_create"),
            {
                "firstname": "Maria",
                "lastname": "Silva",
                "telefone": "11999999999",
                "data_ingresso": "2026-08-10",
            },
        )
        self.assertRedirects(response, reverse("management_members"))
        self.assertTrue(Membros.objects.filter(firstname="Maria", lastname="Silva").exists())

        response = self.client.post(
            reverse("management_user_create"),
            {
                "username": "editor",
                "email": "editor@example.com",
                "first_name": "Editor",
                "last_name": "",
                "password": "senha-segura-123",
                "is_active": "on",
            },
        )
        self.assertRedirects(response, reverse("management_users"))
        editor = User.objects.get(username="editor")
        self.assertTrue(editor.check_password("senha-segura-123"))

        response = self.client.post(
            reverse("management_group_create"),
            {"name": "Editores"},
        )
        self.assertRedirects(response, reverse("management_groups"))
        self.assertTrue(Group.objects.filter(name="Editores").exists())

    def test_superuser_cannot_delete_their_own_account(self):
        response = self.client.post(reverse("management_user_delete", args=[self.superuser.pk]))

        self.assertRedirects(response, reverse("management_users"))
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_editing_own_password_keeps_the_management_session_active(self):
        response = self.client.post(
            reverse("management_user_edit", args=[self.superuser.pk]),
            {
                "username": "admin",
                "email": "admin@example.com",
                "first_name": "",
                "last_name": "",
                "password": "outra-senha-segura-123",
                "is_active": "on",
                "is_staff": "on",
                "is_superuser": "on",
            },
        )

        self.assertRedirects(response, reverse("management_users"))
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.check_password("outra-senha-segura-123"))
        self.assertEqual(
            self.client.get(reverse("management_dashboard")).status_code,
            200,
        )
