from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, DecimalField, F, Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import MembrosForm, ProfileForm, SignupForm
from .models import Favorite, Membros, Recipe, Review


def recipes_with_average():
    return Recipe.objects.annotate(
        average_rating=Coalesce(
            Avg("reviews__rating"),
            F("rating"),
            output_field=DecimalField(max_digits=3, decimal_places=1),
        )
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
    email = request.POST.get("email", "").lower()
    user = authenticate(request, username=email, password=request.POST.get("password", ""))
    if user is None:
        messages.error(request, "E-mail ou senha inválidos.")
        return redirect(f"{reverse('membros')}?auth=login")
    else:
        login(request, user)
        messages.success(request, "Login realizado com sucesso.")
        return redirect("dashboard")


@login_required
def dashboard(request):
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
    return redirect(request.POST.get("next") or "dashboard")


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
    try:
        rating = int(request.POST.get("rating", ""))
    except ValueError:
        rating = 0
    if not 1 <= rating <= 5:
        messages.error(request, "Escolha uma nota entre 1 e 5 estrelas.")
        return redirect("recipe_detail", recipe_id=recipe.id)
    Review.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={"rating": rating, "comment": request.POST.get("comment", "").strip()},
    )
    return redirect("recipe_detail", recipe_id=recipe.id)


@login_required
def profile(request):
    form = ProfileForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Perfil atualizado.")
        return redirect("dashboard")
    return render(request, "profile.html", {"form": form})


@login_required
def signout(request):
    if request.method == "POST":
        logout(request)
    return redirect("membros")

def criar_membros(request):
    if request.method == "POST":
        form = MembrosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_membros')
    else:
        form = MembrosForm()
    return render(request, "criar_membros.html", {"form": form})

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

def deletar_membro(request, id):
    membro = get_object_or_404(Membros, id=id)
    if request.method == 'POST':
        membro.delete()
        return redirect('listar_membros')
    return render(request, "confirmar_deletar.html", {"membro": membro})
