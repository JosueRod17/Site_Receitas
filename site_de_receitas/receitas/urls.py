from django.urls import path

from . import views

urlpatterns = [
    path("", views.listar_membros, name="membros"),
    path("entrar/", views.signin, name="signin"),
    path("criar-conta/", views.signup, name="signup"),
    path("minhas-receitas/", views.dashboard, name="dashboard"),
    path("receitas/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("receitas/<int:recipe_id>/favoritar/", views.toggle_favorite, name="toggle_favorite"),
    path("receitas/<int:recipe_id>/avaliar/", views.review_recipe, name="review_recipe"),
    path("perfil/", views.profile, name="profile"),
    path("sair/", views.signout, name="signout"),
    path("adicionar/", views.criar_membros, name="adicionar_membros"),
    path('criar/', views.criar_membros, name='criar_membro'),
    path('editar/<int:id>/', views.editar_membro, name='editar_membro'),
    path('deletar/<int:id>/', views.deletar_membro, name='deletar_membro'),
    path('membros/', views.listar_membros, name='listar_membros'),
]
