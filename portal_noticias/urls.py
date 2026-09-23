from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Portal de Notícias — Administração"
admin.site.site_title = "Portal de Notícias"
admin.site.index_title = "Painel editorial"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
]
