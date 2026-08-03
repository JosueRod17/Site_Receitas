from django.shortcuts import get_object_or_404, redirect, render

from .forms import MembrosForm
from .models import Membros


def listar_membros(request):
    lista = Membros.objects.all().order_by('firstname')
    return render(request, "index.html", {"membros": lista})

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