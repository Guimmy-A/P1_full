from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Autor(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Post(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "RASCUNHO", "Rascunho"
        EM_REVISAO = "EM_REVISAO", "Em revisão"
        PUBLICADO = "PUBLICADO", "Publicado"
        REJEITADO = "REJEITADO", "Rejeitado"

    # Only these transitions are allowed by the editorial workflow.
    TRANSICOES_VALIDAS = {
        Status.RASCUNHO: {Status.EM_REVISAO},
        Status.EM_REVISAO: {Status.PUBLICADO, Status.REJEITADO},
        Status.REJEITADO: {Status.RASCUNHO},
        Status.PUBLICADO: set(),
    }

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumo = models.CharField(max_length=300, blank=True)
    conteudo = models.TextField()
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="posts")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="posts")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_publicacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("posts:post_detail", kwargs={"slug": self.slug})

    # --- fluxo editorial ---
    def pode_transicionar_para(self, novo_status):
        return novo_status in self.TRANSICOES_VALIDAS.get(self.status, set())

    def _transicionar(self, novo_status, **campos_extra):
        if not self.pode_transicionar_para(novo_status):
            raise ValueError(
                f"Não é possível mudar de '{self.get_status_display()}' "
                f"para '{novo_status}'."
            )
        self.status = novo_status
        for campo, valor in campos_extra.items():
            setattr(self, campo, valor)
        self.save(update_fields=["status", "data_atualizacao", *campos_extra.keys()])

    def enviar_para_revisao(self):
        self._transicionar(self.Status.EM_REVISAO)

    def aprovar(self):
        self._transicionar(self.Status.PUBLICADO, data_publicacao=timezone.now())

    def rejeitar(self):
        self._transicionar(self.Status.REJEITADO)

    def voltar_para_rascunho(self):
        self._transicionar(self.Status.RASCUNHO)


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comentarios")
    nome_autor = models.CharField(max_length=150)
    email_autor = models.EmailField()
    conteudo = models.TextField()
    aprovado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["data_criacao"]

    def __str__(self):
        return f"Comentário de {self.nome_autor} em {self.post.titulo}"
