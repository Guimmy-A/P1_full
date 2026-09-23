from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ComentarioForm, PostForm
from .models import Categoria, Post, Tag


def post_list(request):
    posts = Post.objects.filter(status=Post.Status.PUBLICADO).select_related(
        "autor", "categoria"
    )

    busca = request.GET.get("q", "").strip()
    categoria_slug = request.GET.get("categoria", "")
    tag_slug = request.GET.get("tag", "")

    # Busca e filtro de categoria combinados na mesma consulta com Q(),
    # para poderem ser usados juntos ou separadamente.
    if busca:
        posts = posts.filter(Q(titulo__icontains=busca) | Q(resumo__icontains=busca))

    if categoria_slug:
        posts = posts.filter(categoria__slug=categoria_slug)

    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    posts = posts.distinct()

    paginator = Paginator(posts, 10)
    pagina = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": pagina,
        "categorias": Categoria.objects.all(),
        "tags": Tag.objects.all(),
        "categoria_atual": categoria_slug,
        "tag_atual": tag_slug,
        "busca": busca,
        "filtros_ativos": bool(busca or categoria_slug or tag_slug),
    }
    return render(request, "posts/post_list.html", context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comentarios = post.comentarios.filter(aprovado=True)

    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.save()
            messages.success(request, "Comentário enviado! Ele aparecerá após aprovação.")
            return redirect("posts:post_detail", slug=post.slug)
    else:
        form = ComentarioForm()

    return render(
        request,
        "posts/post_detail.html",
        {"post": post, "comentarios": comentarios, "form": form},
    )


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            messages.success(request, "Post criado como rascunho.")
            return redirect("posts:post_detail", slug=post.slug)
    else:
        form = PostForm()
    return render(request, "posts/post_form.html", {"form": form, "titulo_pagina": "Novo post"})


def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post atualizado.")
            return redirect("posts:post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(
        request,
        "posts/post_form.html",
        {"form": form, "post": post, "titulo_pagina": f"Editar: {post.titulo}"},
    )


def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post excluído.")
        return redirect("posts:post_list")
    return render(request, "posts/post_confirm_delete.html", {"post": post})


def post_enviar_revisao(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(Post, slug=slug)
    try:
        post.enviar_para_revisao()
        messages.success(request, "Post enviado para revisão editorial.")
    except ValueError as erro:
        messages.error(request, str(erro))
    return redirect("posts:post_detail", slug=post.slug)
