# Portal de Notícias — P1 (MVP)

Projeto escolhido do catálogo do laboratório (opção 6 — Blog / Portal de Notícias):
fluxo de publicação com aprovação editorial.

## Por que esse projeto

Os 10 projetos do catálogo têm o mesmo nível de exigência nominal, mas na prática
esse é o que pede a lógica mais enxuta para o P1: nada de cálculo de datas, filas
de espera ou agregações — só CRUD completo + uma máquina de estados simples para
o fluxo editorial. Por isso foi o escolhido para "mais fácil de fazer".

O P2 do catálogo pede API REST em DRF (Django REST Framework), então o projeto já
nasceu em **Django** (e não no FastAPI que você costuma usar), para manter o
mesmo código do P1 até o P2.

## Entidades

- **Categoria** — nome, slug
- **Tag** — nome, slug
- **Autor** — nome, email, bio
- **Post** — título, resumo, conteúdo, autor, categoria, tags, status, datas
- **Comentário** — post, nome/email de quem comenta, conteúdo, aprovado

## Fluxo editorial (P1)

```
RASCUNHO ──enviar_para_revisao()──> EM_REVISAO ──aprovar()──> PUBLICADO
                                         │
                                         └──rejeitar()──> REJEITADO ──voltar_para_rascunho()──> RASCUNHO
```

A validação das transições vive no model (`Post._transicionar`), não nas views nem
no admin — assim qualquer porta de entrada futura (uma API DRF no P2, por exemplo)
reaproveita a mesma regra sem duplicar lógica.

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

## Testes

```bash
python manage.py test posts
```

Cobrem as transições de status (incluindo transições inválidas, como publicar
direto de um rascunho) e as views principais (lista só mostra publicados, detalhe
retorna 200, envio para revisão via POST).

## Estrutura

```
portal_noticias/       # configuração do projeto
posts/
├── models.py           # Categoria, Tag, Autor, Post, Comentário + fluxo editorial
├── admin.py             # área editorial com ações de aprovar/rejeitar em lote
├── forms.py              # formulários de post e comentário
├── views.py               # CRUD de post + fluxo público
├── urls.py
├── tests.py
├── management/commands/seed_dados.py
└── templates/posts/
```

## Próximos passos (P2 — Aula 20)

Segundo o catálogo: multi-organização (múltiplos blogs), papéis de usuário
(autor/editor/leitor), dashboard e API REST em DRF. Como as regras de negócio já
estão nos models e não nas views, dá para plugar o DRF por cima do que já existe
sem reescrever a lógica do P1.
