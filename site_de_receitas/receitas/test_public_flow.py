from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Recipe, Review
from .views import recipes_with_average


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="member-login",
            email="member@example.com",
            first_name="Member",
            password="senha-segura-123",
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="senha-segura-123",
        )

    def test_member_can_sign_in_with_email_when_username_is_different(self):
        response = self.client.post(
            reverse("signin"),
            {"identifier": "member@example.com", "password": "senha-segura-123"},
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.member.pk))

    def test_superuser_can_sign_in_with_username_and_reaches_management(self):
        response = self.client.post(
            reverse("signin"),
            {"identifier": "admin", "password": "senha-segura-123"},
        )

        self.assertRedirects(response, reverse("management_dashboard"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.superuser.pk))

    def test_profile_page_displays_and_updates_email(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("profile"))
        self.assertContains(response, "member@example.com")

        response = self.client.post(
            reverse("profile"),
            {
                "nickname": "Novo nome",
                "email": "novo@example.com",
                "current_password": "senha-segura-123",
                "new_password1": "",
                "new_password2": "",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.email, "novo@example.com")


class FeedbackRatingTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="senha-segura-123",
        )
        self.recipe = Recipe.objects.create(
            title="Receita sem feedback",
            category="Teste",
            image_url="https://example.com/recipe.jpg",
            prep_time=20,
            difficulty="Fácil",
            rating=4.5,
        )

    def test_recipe_without_feedback_has_no_public_rating(self):
        recipe = recipes_with_average().get(pk=self.recipe.pk)

        self.assertIsNone(recipe.average_rating)
        self.assertEqual(recipe.review_count, 0)

        response = self.client.get(reverse("membros"))
        self.assertContains(response, "Sem avaliações")
        self.assertNotContains(response, 'class="tag"')

    def test_average_and_count_come_from_feedbacks(self):
        second_user = User.objects.create_user(
            username="second",
            email="second@example.com",
            password="senha-segura-123",
        )
        Review.objects.create(user=self.author, recipe=self.recipe, rating=3)
        Review.objects.create(user=second_user, recipe=self.recipe, rating=5)

        recipe = recipes_with_average().get(pk=self.recipe.pk)

        self.assertEqual(recipe.average_rating, 4)
        self.assertEqual(recipe.review_count, 2)
        response = self.client.get(reverse("recipe_detail", args=[self.recipe.pk]))
        self.assertContains(response, "4.0/5")
        self.assertContains(response, "2 avaliações")

    def test_feedback_rejects_comment_larger_than_the_allowed_limit(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("review_recipe", args=[self.recipe.pk]),
            {"rating": 5, "comment": "x" * 1001},
            follow=True,
        )

        self.assertFalse(Review.objects.filter(user=self.author, recipe=self.recipe).exists())
        self.assertContains(response, "Revise a nota e o comentário antes de publicar.")

    def test_favorite_does_not_redirect_to_an_external_posted_url(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("toggle_favorite", args=[self.recipe.pk]),
            {"next": "https://example.org/untrusted"},
        )

        self.assertRedirects(response, reverse("dashboard"))
