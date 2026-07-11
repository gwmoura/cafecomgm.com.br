#### cronjob

0 9 * * * cd /caminho/para/cafe-blog-ai/contentgenerator && /caminho/para/venv/bin/python scheduler.py >> logs.txt 2>&1

O `cd` precisa cair dentro de `contentgenerator/` (os caminhos usados pelos scripts são relativos a essa pasta), mas o `scheduler.py` faz `git add`/`git commit` na raiz do repositório automaticamente.

#### O que o `scheduler.py` faz em cada execução (pensado para rodar 1x/dia via cron)

1. **Repõe temas**: para cada categoria com menos de 3 temas ainda não usados, chama `topic_researcher.py` para pesquisar mais via LLM antes de sortear.
2. **Escolhe e escreve**: sorteia um tema não usado (ou pesquisa um novo, se tudo estiver esgotado) e gera o artigo com `writer.py`.
3. **Revisa**: roda `proofreader.py` sobre o artigo gerado. Se o `score` retornado for menor que 6/10, o post **não é publicado** — fica em `outputs/` para ajuste manual (`make rewrite`), e o tema segue marcado como usado (o próximo run sorteia outro tema).
4. **Publica localmente**: se aprovado na revisão, converte o artigo em post Hugo (`post_writer.py`) em `content/posts/` e faz `git commit` (apenas local — **não** dá `git push` automaticamente).

Isso significa que o bot roda sozinho todo dia, mas a publicação real no site continua sendo um passo manual seu: um `git push` para a `master` (o Cloudflare Pages builda e publica sozinho a partir daí), para você revisar o conteúdo antes de ir ao ar.

#### Como funciona o controle de temas repetidos

- `topics/<categoria>.txt` continua sendo a lista mestra de temas por categoria (inclui `receitas.txt`, além de `cafe_geral`, `curiosidades`, `equipamentos` e `metodos`).
- `topics/.usados.json` é o registro (gerado automaticamente) de quais temas já viraram artigo, com data e arquivo gerado.
- `scheduler.py` só sorteia temas que ainda não estão em `.usados.json`. Ao gerar um artigo com sucesso, o tema é marcado como usado.
- Se todas as categorias estiverem esgotadas, o `scheduler.py` aciona `topic_researcher.py` automaticamente para pesquisar novos temas via LLM e adicioná-los ao arquivo da categoria antes de continuar.
- `topic_researcher.py` também pode ser rodado manualmente (`make research-topics`) para engordar as listas de temas sob demanda, para uma categoria específica ou para todas.
