from django import forms

from .models import Comentario, Post


class PostForm(forms.ModelForm):
    CONTEUDO_MIN_CARACTERES = 50

    class Meta:
        model = Post
        fields = ["titulo", "resumo", "conteudo", "autor", "categoria", "tags"]
        widgets = {
            "resumo": forms.Textarea(attrs={"rows": 2}),
            "conteudo": forms.Textarea(attrs={"rows": 12}),
        }

    def clean_conteudo(self):
        conteudo = self.cleaned_data.get("conteudo", "")
        if len(conteudo.strip()) < self.CONTEUDO_MIN_CARACTERES:
            raise forms.ValidationError(
                f"O conteúdo do post deve ter pelo menos "
                f"{self.CONTEUDO_MIN_CARACTERES} caracteres para ser publicado."
            )
        return conteudo


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["nome_autor", "email_autor", "conteudo"]
        widgets = {
            "conteudo": forms.Textarea(attrs={"rows": 4}),
        }
