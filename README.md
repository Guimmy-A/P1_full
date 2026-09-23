# 📰 Portal de Notícias

> Sistema de publicação de notícias com fluxo editorial (rascunho → revisão → publicado),
> construído em Django como projeto da disciplina **Laboratório de Programação Full Stack**
> (Universidade de Vassouras).

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)
![Status](https://img.shields.io/badge/status-P1%20entregue-success)

Projeto escolhido do catálogo do laboratório (opção 6 — Blog / Portal de Notícias):
fluxo de publicação com aprovação editorial.

## ✨ Funcionalidades

| | |
|---|---|
| ✅ | CRUD completo de posts, categorias, tags, autores e comentários |
| ✅ | Fluxo editorial com máquina de estados (rascunho → revisão → publicado/rejeitado) |
| 🔎 | **Busca por texto** (título e resumo) na listagem, combinável com filtro |
| 🏷️ | **Filtro por categoria** via `<select>`, usando `Q()` para combinar com a busca |
| ✔️ | **Validação customizada**: post não pode ser publicado com menos de 50 caracteres de conteúdo |
| 💬 | Comentários com moderação (só aparecem depois de aprovados no admin) |
| 🛠️ | Área administrativa com ações em lote (aprovar/rejeitar posts) |

## Fluxo editorial

RASCUNHO ──enviar_para_revisao()──> EM_REVISAO ──aprovar()──> PUBLICADO
│
└──rejeitar()──> REJEITADO ──voltar_para_rascunho()──> RASCUNHO



A validação das transições vive no model (`Post._transicionar`), não nas views nem
no admin.

- Autores criam/editam posts pelas telas públicas (`/novo/`, `/<slug>/editar/`) —
  todo post novo nasce como **rascunho**.
- O próprio autor pode "enviar para revisão" pela página do post.
- A aprovação editorial (aprovar/rejeitar) é feita pela equipe editorial no
  **admin** (`/admin/`), com ações em lote na lista de posts.
- Comentários entram como não aprovados e só aparecem no post depois de moderados
  no admin.

## Como rodar

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_dados       # cria categorias, autores, posts e comentários de exemplo
python manage.py createsuperuser  # opcional, para entrar em /admin/

python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para o portal público e
`http://127.0.0.1:8000/admin/` para a área editorial.

O banco `db.sqlite3` já vem neste zip com os dados do `seed_dados` — se preferir
começar do zero, é só apagá-lo antes do `migrate`.

## 🔎 Feature 1 — Busca e filtro na listagem

Na página inicial (`/`), o formulário de busca permite:

- **Buscar por texto**, procurando no título e no resumo do post (`icontains`, sem
  diferenciar maiúsculas/minúsculas).
- **Filtrar por categoria**, via `<select>`.
- Os dois filtros funcionam **juntos ou separadamente**, combinados na mesma
  consulta com `Q()` do Django:

```python
  if busca:
      posts = posts.filter(Q(titulo__icontains=busca) | Q(resumo__icontains=busca))
  if categoria_slug:
      posts = posts.filter(categoria__slug=categoria_slug)
```

- O campo de busca permanece preenchido com o termo digitado após a pesquisa.
- Quando a busca/filtro não retorna nenhum post, aparece uma mensagem específica
  ("Nenhum post encontrado para esses filtros"), diferente da mensagem exibida
  quando simplesmente não há posts publicados ainda.

## ✔️ Feature 2 — Validação customizada no formulário

O `PostForm` (`posts/forms.py`) sobrescreve `clean_conteudo()` para impedir que um
post seja salvo com um conteúdo muito curto:

```python
def clean_conteudo(self):
    conteudo = self.cleaned_data.get("conteudo", "")
    if len(conteudo.strip()) < self.CONTEUDO_MIN_CARACTERES:
        raise forms.ValidationError(
            "O conteúdo do post deve ter pelo menos 50 caracteres para ser publicado."
        )
    return conteudo
```

**Por que essa regra?** Sem ela, qualquer rascunho de uma linha poderia seguir para
publicação, esvaziando o propósito do fluxo editorial do projeto — o conteúdo é o
que justifica a existência do post.

## Testes

```bash
python manage.py test posts
```

Cobrem as transições de status (incluindo transições inválidas, como publicar
direto de um rascunho) e as views principais (lista só mostra publicados, detalhe
retorna 200, envio para revisão via POST).

## Estrutura

## Estrutura

portal_noticias/ # configuração do projeto
posts/
├── models.py # Categoria, Tag, Autor, Post, Comentário + fluxo editorial
├── admin.py # área editorial com ações de aprovar/rejeitar em lote
├── forms.py # formulários de post e comentário
├── views.py # CRUD de post + fluxo público
├── urls.py
├── tests.py
├── management/commands/seed_dados.py
└── templates/posts/


