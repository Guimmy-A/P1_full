from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("novo/", views.post_create, name="post_create"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
    path("<slug:slug>/editar/", views.post_update, name="post_update"),
    path("<slug:slug>/excluir/", views.post_delete, name="post_delete"),
    path("<slug:slug>/enviar-revisao/", views.post_enviar_revisao, name="post_enviar_revisao"),
]
