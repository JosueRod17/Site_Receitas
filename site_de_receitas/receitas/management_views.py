from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .access import superuser_required
from .management_forms import (
    FavoriteManagementForm,
    GroupManagementForm,
    MemberManagementForm,
    RecipeManagementForm,
    ReviewManagementForm,
    UserManagementForm,
)
from .models import Favorite, Membros, Recipe, Review


def _page(request, queryset, per_page=16):
    return Paginator(queryset, per_page).get_page(request.GET.get("page"))


def _query(request):
    return request.GET.get("q", "").strip()


def _list_response(request, *, section, page_title, queryset, query):
    return render(
        request,
        "management/object_list.html",
        {
            "section": section,
            "page_title": page_title,
            "page_obj": _page(request, queryset),
            "query": query,
        },
    )


def _form_response(
    request,
    *,
    section,
    page_title,
    form_class,
    list_url,
    instance=None,
    actor=None,
):
    form_kwargs = {"instance": instance} if instance is not None else {}
    if form_class is UserManagementForm:
        form_kwargs["actor"] = actor
    form = form_class(request.POST or None, **form_kwargs)
    if request.method == "POST" and form.is_valid():
        saved_object = form.save()
        if form_class is UserManagementForm and saved_object.pk == request.user.pk:
            update_session_auth_hash(request, saved_object)
        messages.success(request, "Alterações salvas com sucesso.")
        return redirect(list_url)
    return render(
        request,
        "management/object_form.html",
        {
            "section": section,
            "page_title": page_title,
            "form": form,
            "cancel_url": list_url,
        },
    )


@superuser_required
def dashboard(request):
    top_recipes = (
        Recipe.objects.annotate(
            average_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
        )
        .order_by("-review_count", "-average_rating", "title")[:6]
    )
    latest_reviews = Review.objects.select_related("recipe", "user")[:6]
    stats = [
        {"label": "Receitas", "value": Recipe.objects.count(), "url": "management_recipes"},
        {"label": "Avaliações", "value": Review.objects.count(), "url": "management_reviews"},
        {"label": "Favoritos", "value": Favorite.objects.count(), "url": "management_favorites"},
        {"label": "Membros", "value": Membros.objects.count(), "url": "management_members"},
        {"label": "Usuários", "value": User.objects.count(), "url": "management_users"},
        {"label": "Grupos", "value": Group.objects.count(), "url": "management_groups"},
    ]
    return render(
        request,
        "management/dashboard.html",
        {
            "page_title": "Visão geral",
            "section": "dashboard",
            "stats": stats,
            "top_recipes": top_recipes,
            "latest_reviews": latest_reviews,
        },
    )


@superuser_required
def recipes(request):
    query = _query(request)
    queryset = Recipe.objects.annotate(
        average_rating=Avg("reviews__rating"), review_count=Count("reviews")
    )
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(category__icontains=query))
    return _list_response(
        request,
        section="recipes",
        page_title="Receitas",
        queryset=queryset.order_by("-created_at", "title"),
        query=query,
    )


@superuser_required
def recipe_create(request):
    return _form_response(
        request,
        section="recipes",
        page_title="Nova receita",
        form_class=RecipeManagementForm,
        list_url="management_recipes",
    )


@superuser_required
def recipe_edit(request, recipe_id):
    return _form_response(
        request,
        section="recipes",
        page_title="Editar receita",
        form_class=RecipeManagementForm,
        list_url="management_recipes",
        instance=get_object_or_404(Recipe, pk=recipe_id),
    )


@require_POST
@superuser_required
def recipe_delete(request, recipe_id):
    get_object_or_404(Recipe, pk=recipe_id).delete()
    messages.success(request, "Receita removida.")
    return redirect("management_recipes")


@superuser_required
def reviews(request):
    query = _query(request)
    queryset = Review.objects.select_related("recipe", "user")
    if query:
        queryset = queryset.filter(
            Q(recipe__title__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
            | Q(comment__icontains=query)
        )
    return _list_response(
        request,
        section="reviews",
        page_title="Avaliações",
        queryset=queryset,
        query=query,
    )


@superuser_required
def review_create(request):
    return _form_response(
        request,
        section="reviews",
        page_title="Nova avaliação",
        form_class=ReviewManagementForm,
        list_url="management_reviews",
    )


@superuser_required
def review_edit(request, review_id):
    return _form_response(
        request,
        section="reviews",
        page_title="Editar avaliação",
        form_class=ReviewManagementForm,
        list_url="management_reviews",
        instance=get_object_or_404(Review, pk=review_id),
    )


@require_POST
@superuser_required
def review_delete(request, review_id):
    get_object_or_404(Review, pk=review_id).delete()
    messages.success(request, "Avaliação removida.")
    return redirect("management_reviews")


@superuser_required
def favorites(request):
    query = _query(request)
    queryset = Favorite.objects.select_related("recipe", "user")
    if query:
        queryset = queryset.filter(
            Q(recipe__title__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__email__icontains=query)
        )
    return _list_response(
        request,
        section="favorites",
        page_title="Favoritos",
        queryset=queryset.order_by("-created_at"),
        query=query,
    )


@superuser_required
def favorite_create(request):
    return _form_response(
        request,
        section="favorites",
        page_title="Novo favorito",
        form_class=FavoriteManagementForm,
        list_url="management_favorites",
    )


@superuser_required
def favorite_edit(request, favorite_id):
    return _form_response(
        request,
        section="favorites",
        page_title="Editar favorito",
        form_class=FavoriteManagementForm,
        list_url="management_favorites",
        instance=get_object_or_404(Favorite, pk=favorite_id),
    )


@require_POST
@superuser_required
def favorite_delete(request, favorite_id):
    get_object_or_404(Favorite, pk=favorite_id).delete()
    messages.success(request, "Favorito removido.")
    return redirect("management_favorites")


@superuser_required
def members(request):
    query = _query(request)
    queryset = Membros.objects.all()
    if query:
        filters = Q(firstname__icontains=query) | Q(lastname__icontains=query)
        if query.isdigit():
            filters |= Q(telefone=int(query))
        queryset = queryset.filter(filters)
    return _list_response(
        request,
        section="members",
        page_title="Membros",
        queryset=queryset.order_by("firstname", "lastname"),
        query=query,
    )


@superuser_required
def member_create(request):
    return _form_response(
        request,
        section="members",
        page_title="Novo membro",
        form_class=MemberManagementForm,
        list_url="management_members",
    )


@superuser_required
def member_edit(request, member_id):
    return _form_response(
        request,
        section="members",
        page_title="Editar membro",
        form_class=MemberManagementForm,
        list_url="management_members",
        instance=get_object_or_404(Membros, pk=member_id),
    )


@require_POST
@superuser_required
def member_delete(request, member_id):
    get_object_or_404(Membros, pk=member_id).delete()
    messages.success(request, "Membro removido.")
    return redirect("management_members")


@superuser_required
def users(request):
    query = _query(request)
    queryset = User.objects.prefetch_related("groups")
    if query:
        queryset = queryset.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
    return _list_response(
        request,
        section="users",
        page_title="Usuários",
        queryset=queryset.order_by("username"),
        query=query,
    )


@superuser_required
def user_create(request):
    return _form_response(
        request,
        section="users",
        page_title="Novo usuário",
        form_class=UserManagementForm,
        list_url="management_users",
        actor=request.user,
    )


@superuser_required
def user_edit(request, user_id):
    return _form_response(
        request,
        section="users",
        page_title="Editar usuário",
        form_class=UserManagementForm,
        list_url="management_users",
        instance=get_object_or_404(User, pk=user_id),
        actor=request.user,
    )


@require_POST
@superuser_required
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.pk == request.user.pk:
        messages.error(request, "Você não pode excluir sua própria conta administrativa.")
    else:
        user.delete()
        messages.success(request, "Usuário removido.")
    return redirect("management_users")


@superuser_required
def groups(request):
    query = _query(request)
    queryset = Group.objects.annotate(
        member_count=Count("user", distinct=True),
        permission_count=Count("permissions", distinct=True),
    )
    if query:
        queryset = queryset.filter(name__icontains=query)
    return _list_response(
        request,
        section="groups",
        page_title="Grupos e permissões",
        queryset=queryset.order_by("name"),
        query=query,
    )


@superuser_required
def group_create(request):
    return _form_response(
        request,
        section="groups",
        page_title="Novo grupo",
        form_class=GroupManagementForm,
        list_url="management_groups",
    )


@superuser_required
def group_edit(request, group_id):
    return _form_response(
        request,
        section="groups",
        page_title="Editar grupo",
        form_class=GroupManagementForm,
        list_url="management_groups",
        instance=get_object_or_404(Group, pk=group_id),
    )


@require_POST
@superuser_required
def group_delete(request, group_id):
    get_object_or_404(Group, pk=group_id).delete()
    messages.success(request, "Grupo removido.")
    return redirect("management_groups")
