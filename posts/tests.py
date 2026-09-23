from django.test import TestCase
from django.urls import reverse

from .models import Autor, Categoria, Post


class PostTransicaoTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Teste", email="autor@teste.com")
        self.categoria = Categoria.objects.create(nome="Categoria Teste")
        self.post = Post.objects.create(
            titulo="Post de teste",
            conteudo="Conteúdo",
            autor=self.autor,
            categoria=self.categoria,
        )

    def test_post_comeca_como_rascunho(self):
        self.assertEqual(self.post.status, Post.Status.RASCUNHO)

    def test_fluxo_editorial_completo(self):
        self.post.enviar_para_revisao()
        self.assertEqual(self.post.status, Post.Status.EM_REVISAO)

        self.post.aprovar()
        self.assertEqual(self.post.status, Post.Status.PUBLICADO)
        self.assertIsNotNone(self.post.data_publicacao)

    def test_nao_pode_publicar_direto_do_rascunho(self):
        with self.assertRaises(ValueError):
            self.post.aprovar()

    def test_post_rejeitado_pode_voltar_a_rascunho(self):
        self.post.enviar_para_revisao()
        self.post.rejeitar()
        self.assertEqual(self.post.status, Post.Status.REJEITADO)

        self.post.voltar_para_rascunho()
        self.assertEqual(self.post.status, Post.Status.RASCUNHO)

    def test_publicado_e_estado_terminal(self):
        self.post.enviar_para_revisao()
        self.post.aprovar()
        with self.assertRaises(ValueError):
            self.post.rejeitar()


class PostViewsTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Teste", email="autor2@teste.com")
        self.categoria = Categoria.objects.create(nome="Categoria Teste 2")
        self.post_publicado = Post.objects.create(
            titulo="Post Publicado",
            conteudo="Conteúdo publicado",
            autor=self.autor,
            categoria=self.categoria,
            status=Post.Status.PUBLICADO,
        )
        self.post_rascunho = Post.objects.create(
            titulo="Post Rascunho",
            conteudo="Conteúdo em rascunho",
            autor=self.autor,
            categoria=self.categoria,
            status=Post.Status.RASCUNHO,
        )

    def test_lista_mostra_apenas_publicados(self):
        response = self.client.get(reverse("posts:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post Publicado")
        self.assertNotContains(response, "Post Rascunho")

    def test_detalhe_do_post(self):
        response = self.client.get(
            reverse("posts:post_detail", kwargs={"slug": self.post_publicado.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_enviar_para_revisao_via_post(self):
        response = self.client.post(
            reverse("posts:post_enviar_revisao", kwargs={"slug": self.post_rascunho.slug})
        )
        self.post_rascunho.refresh_from_db()
        self.assertEqual(self.post_rascunho.status, Post.Status.EM_REVISAO)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"slug": self.post_rascunho.slug}),
        )
