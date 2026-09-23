from django.core.management.base import BaseCommand
from django.utils import timezone

from posts.models import Autor, Categoria, Comentario, Post, Tag


class Command(BaseCommand):
    help = "Popula o banco com dados de exemplo para demonstração do P1."

    def handle(self, *args, **options):
        if Post.objects.exists():
            self.stdout.write(self.style.WARNING("Já existem posts. Nada foi criado."))
            return

        ana = Autor.objects.create(
            nome="Ana Souza", email="ana.souza@exemplo.com", bio="Editora de tecnologia."
        )
        bruno = Autor.objects.create(
            nome="Bruno Lima", email="bruno.lima@exemplo.com", bio="Repórter de economia."
        )

        tecnologia = Categoria.objects.create(nome="Tecnologia")
        economia = Categoria.objects.create(nome="Economia")
        cultura = Categoria.objects.create(nome="Cultura")

        tag_python = Tag.objects.create(nome="Python")
        tag_mercado = Tag.objects.create(nome="Mercado")
        tag_django = Tag.objects.create(nome="Django")

        post1 = Post.objects.create(
            titulo="Como a IA está mudando o desenvolvimento de software",
            resumo="Um panorama sobre ferramentas de IA no dia a dia de quem programa.",
            conteudo=(
                "Conteúdo de exemplo sobre inteligência artificial aplicada ao "
                "desenvolvimento de software, cobrindo produtividade e novas "
                "ferramentas usadas por times de engenharia."
            ),
            autor=ana,
            categoria=tecnologia,
            status=Post.Status.PUBLICADO,
            data_publicacao=timezone.now(),
        )
        post1.tags.set([tag_python, tag_django])

        post2 = Post.objects.create(
            titulo="Mercado de trabalho para desenvolvedores em 2026",
            resumo="Tendências de contratação e principais tecnologias em alta.",
            conteudo=(
                "Conteúdo de exemplo sobre o mercado de trabalho para "
                "desenvolvedores, aguardando revisão editorial antes da publicação."
            ),
            autor=bruno,
            categoria=economia,
            status=Post.Status.EM_REVISAO,
        )
        post2.tags.set([tag_mercado])

        Post.objects.create(
            titulo="Ideias para a próxima matéria de cultura",
            conteudo="Rascunho ainda em construção...",
            autor=ana,
            categoria=cultura,
            status=Post.Status.RASCUNHO,
        )

        Comentario.objects.create(
            post=post1,
            nome_autor="Leitor Curioso",
            email_autor="leitor@exemplo.com",
            conteudo="Ótima matéria, muito esclarecedora!",
            aprovado=True,
        )
        Comentario.objects.create(
            post=post1,
            nome_autor="Outro Leitor",
            email_autor="outro@exemplo.com",
            conteudo="Aguardando moderação.",
            aprovado=False,
        )

        self.stdout.write(self.style.SUCCESS("Dados de exemplo criados com sucesso."))
