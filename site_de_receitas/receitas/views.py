from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .access import superuser_required
from .forms import MembrosForm, ProfileForm, RecipeReviewForm, SignupForm
from .models import Favorite, Membros, Recipe, Review


def recipes_with_average():
    return Recipe.objects.annotate(
        average_rating=Avg("reviews__rating"),
        review_count=Count("reviews"),
    )


def filtered_recipes(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "recent")
    recipes = recipes_with_average()
    if query:
        recipes = recipes.filter(Q(title__icontains=query) | Q(category__icontains=query))
    if category:
        recipes = recipes.filter(category=category)
    ordering = {"easy": "prep_time", "rated": "-average_rating"}.get(sort, "-created_at")
    return recipes.order_by(ordering), query, category, sort


def listar_membros(request):
    recipes, query, category, _ = filtered_recipes(request)
    return render(request, "index.html", {
        "recipes": recipes,
        "query": query,
        "active_category": category,
        "categories": Recipe.objects.values("category").annotate(total=Count("id")).order_by("category"),
    })


def signup(request):
    if request.method != "POST":
        return redirect("membros")
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Conta criada com sucesso.")
        return redirect("dashboard")
    else:
        messages.error(request, "Não foi possível criar a conta. Verifique os dados.")
    return redirect(f"{reverse('membros')}?auth=signup")


def signin(request):
    if request.method != "POST":
        return redirect("membros")
    identifier = request.POST.get("identifier", request.POST.get("email", "")).strip()
    password = request.POST.get("password", "")
    user = authenticate(request, username=identifier, password=password)
    if user is None and identifier:
        matches = list(
            User.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            ).distinct()[:2]
        )
        if len(matches) == 1:
            user = authenticate(request, username=matches[0].username, password=password)
    if user is None:
        messages.error(request, "E-mail, usuário ou senha inválidos.")
        return redirect(f"{reverse('membros')}?auth=login")
    else:
        login(request, user)
        messages.success(request, "Login realizado com sucesso.")
        return redirect("management_dashboard" if user.is_superuser else "dashboard")


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect("management_dashboard")
    recipes, query, category, sort = filtered_recipes(request)
    favorite_ids = set(request.user.favorite_recipes.values_list("recipe_id", flat=True))
    return render(request, "dashboard.html", {
        "recipes": recipes,
        "favorite_ids": favorite_ids,
        "query": query,
        "active_category": category,
        "sort": sort,
        "categories": Recipe.objects.values("category").annotate(total=Count("id")).order_by("category"),
    })


@login_required
def toggle_favorite(request, recipe_id):
    if request.method != "POST":
        return redirect("dashboard")
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        favorite.delete()
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("dashboard")


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(recipes_with_average(), id=recipe_id)
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, recipe=recipe).exists()
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, recipe=recipe).first()
    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "is_favorite": is_favorite,
        "reviews": recipe.reviews.select_related("user"),
        "user_review": user_review,
    })


@login_required
def review_recipe(request, recipe_id):
    if request.method != "POST":
        return redirect("recipe_detail", recipe_id=recipe_id)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipeReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Revise a nota e o comentário antes de publicar.")
        return redirect("recipe_detail", recipe_id=recipe.id)
    Review.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={"rating": form.cleaned_data["rating"], "comment": form.cleaned_data["comment"].strip()},
    )
    messages.success(request, "Avaliação publicada.")
    return redirect("recipe_detail", recipe_id=recipe.id)


@login_required
def profile(request):
    form = ProfileForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Perfil atualizado.")
        return redirect("management_dashboard" if user.is_superuser else "dashboard")
    return render(request, "profile.html", {
        "form": form,
        "back_url_name": "management_dashboard" if request.user.is_superuser else "dashboard",
    })


@login_required
def signout(request):
    if request.method == "POST":
        logout(request)
    return redirect("membros")

@superuser_required
def criar_membros(request):
    if request.method == "POST":
        form = MembrosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_membros')
    else:
        form = MembrosForm()
    return render(request, "criar_membros.html", {"form": form})

@superuser_required
def editar_membro(request, id):
    membro = get_object_or_404(Membros, id=id)
    if request.method == "POST":
        form = MembrosForm(request.POST, instance=membro)
        if form.is_valid():
            form.save()
            return redirect('listar_membros')
    else:
        form = MembrosForm(instance=membro)
    return render(request, "editar_membros.html", {"form": form, "membro": membro})

@superuser_required
def deletar_membro(request, id):
    membro = get_object_or_404(Membros, id=id)
    if request.method == 'POST':
        membro.delete()
        return redirect('listar_membros')
    return render(request, "confirmar_deletar.html", {"membro": membro})
