from django.contrib import admin
from django.utils.translation import ngettext

from .models import Autor, Categoria, Comentario, Post, Tag


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome",)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email")
    search_fields = ("nome", "email")


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    fields = ("nome_autor", "email_autor", "conteudo", "aprovado", "data_criacao")
    readonly_fields = ("data_criacao",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "categoria", "status", "data_criacao", "data_publicacao")
    list_filter = ("status", "categoria", "tags")
    search_fields = ("titulo", "conteudo")
    prepopulated_fields = {"slug": ("titulo",)}
    autocomplete_fields = ("autor", "categoria", "tags")
    readonly_fields = ("data_criacao", "data_atualizacao", "data_publicacao")
    inlines = [ComentarioInline]
    actions = ["acao_enviar_para_revisao", "acao_aprovar", "acao_rejeitar"]

    def _aplicar_transicao(self, request, queryset, metodo, msg_singular, msg_plural):
        sucesso = 0
        for post in queryset:
            try:
                getattr(post, metodo)()
                sucesso += 1
            except ValueError as erro:
                self.message_user(request, f"{post}: {erro}", level="warning")
        if sucesso:
            self.message_user(request, ngettext(msg_singular, msg_plural, sucesso) % sucesso)

    @admin.action(description="Enviar selecionados para revisão")
    def acao_enviar_para_revisao(self, request, queryset):
        self._aplicar_transicao(
            request, queryset, "enviar_para_revisao",
            "%d post enviado para revisão.", "%d posts enviados para revisão.",
        )

    @admin.action(description="Aprovar e publicar selecionados")
    def acao_aprovar(self, request, queryset):
        self._aplicar_transicao(
            request, queryset, "aprovar",
            "%d post publicado.", "%d posts publicados.",
        )

    @admin.action(description="Rejeitar selecionados")
    def acao_rejeitar(self, request, queryset):
        self._aplicar_transicao(
            request, queryset, "rejeitar",
            "%d post rejeitado.", "%d posts rejeitados.",
        )


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("nome_autor", "post", "aprovado", "data_criacao")
    list_filter = ("aprovado",)
    search_fields = ("nome_autor", "email_autor", "conteudo")
    actions = ["aprovar_comentarios"]

    @admin.action(description="Aprovar comentários selecionados")
    def aprovar_comentarios(self, request, queryset):
        atualizados = queryset.update(aprovado=True)
        self.message_user(request, f"{atualizados} comentário(s) aprovado(s).")
