from django.urls import path

from . import views

urlpatterns = [
    path("", views.listar_membros, name="membros"),
    path("adicionar/", views.criar_membros, name="adicionar_membros"),
    path('criar/', views.criar_membros, name='criar_membro'),
    path('editar/<int:id>/', views.editar_membro, name='editar_membro'),
    path('deletar/<int:id>/', views.deletar_membro, name='deletar_membro'),
    path('membros/', views.listar_membros, name='listar_membros'),
]