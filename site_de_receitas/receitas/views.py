from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MembrosForm, SignupForm
from .models import Membros, Recipe


def listar_membros(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(Q(title__icontains=query) | Q(category__icontains=query))
    if category:
        recipes = recipes.filter(category=category)
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
    else:
        messages.error(request, "Não foi possível criar a conta. Verifique os dados.")
    return redirect("membros")


def signin(request):
    if request.method != "POST":
        return redirect("membros")
    email = request.POST.get("email", "").lower()
    user = authenticate(request, username=email, password=request.POST.get("password", ""))
    if user is None:
        messages.error(request, "E-mail ou senha inválidos.")
    else:
        login(request, user)
        messages.success(request, "Login realizado com sucesso.")
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
