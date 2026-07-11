# Café com GM

Blog sobre café ([cafecom.georgemoura.com.br](https://cafecom.georgemoura.com.br)) com receitas, boas práticas, curiosidades e equipamentos. O site é gerado com [Hugo](https://gohugo.io/) e o conteúdo é escrito por um pipeline de geração de artigos com LLM que roda de forma (semi-)automática.

O repositório tem duas partes:

1. **Site Hugo** (raiz) — o blog em si.
2. **[`contentgenerator/`](contentgenerator/)** — ferramental Python que usa um LLM (via LangChain, Ollama ou OpenAI) para pesquisar tópicos, escrever, revisar e publicar artigos como posts do Hugo.

## Site Hugo

- Config: [`config.toml`](config.toml). Tema ativo: `story` (`themes/story`).
- Posts ficam em `content/posts/*.md`, com front matter padrão do Hugo (`title`, `date`, `description`, `keywords`, `draft`).
- `layouts/` só contém overrides sobre o tema: `layouts/_default/baseof.html` e partials do Google Analytics/AdSense (`layouts/partials/google/`).
- `public/` é a saída do build e `resources/_gen` é o cache de recursos do Hugo — ambos são artefatos de build, não código-fonte.
- **Deploy é automático**: o site é publicado via **Cloudflare Pages/Workers**, que builda e publica sozinho a cada push na branch `master`. Não é preciso rodar nenhum comando de deploy manualmente. (O bloco `[deployment]` em `config.toml`, apontando para um bucket GCS, é legado e não é mais usado.)
- `static/ads.txt` declara o publisher ID do Google AdSense (`pub-7444396631758040`) — arquivo exigido pelo Google para o site conseguir servir anúncios.

Comandos comuns:

```bash
hugo server -D   # servidor local, incluindo rascunhos (draft: true)
hugo             # builda o site estático em public/ (útil para pré-visualizar; o Cloudflare builda sozinho no push)
```

## `contentgenerator/` — pipeline de artigos

Scripts Python independentes (sem um CLI único — cada arquivo é rodado diretamente com `python3 <arquivo>.py`). O diretório de trabalho precisa ser `contentgenerator/`, pois os caminhos (`prompts/`, `outputs/`, `revisions/`, `topics/`) são relativos a ele.

### Instalação

```bash
cd contentgenerator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` dentro de `contentgenerator/` com as variáveis do LLM que você quer usar:

```bash
# Usando Ollama (local, grátis)
LLM=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OU usando OpenAI (pago)
LLM=chatgpt
OPENAI_API_KEY=sk-...
OPENAI_MODEL=o4-mini
```

Qualquer valor de `LLM` diferente de `ollama` usa a OpenAI — então tome cuidado, cada execução automática do bot (pesquisa de tópicos + artigo + revisão) gera chamadas pagas à API quando `LLM` não é `ollama`.

### Scripts disponíveis

| Comando | O que faz |
|---|---|
| `make write` (`python3 writer.py`) | Gera um novo artigo a partir de um tópico digitado na hora, salva em `outputs/`. |
| `make rewrite` (`python3 rewriter.py`) | Regenera um rascunho existente em `outputs/` aplicando mudanças pedidas. |
| `make revise` (`python3 proofreader.py`) | Revisa um artigo e salva um parecer em JSON (`score` 0-10 + comentários) em `revisions/`. |
| `make consultant` (`python3 consultant.py`) | Bate-papo livre com a persona "entusiasta de café" do blog. |
| `make research-topics` (`python3 topic_researcher.py`) | Pede ao LLM novos tópicos para uma categoria (ou todas) e adiciona em `topics/<categoria>.txt`, sem repetir o que já existe. |
| `python3 post_writer.py` | Converte um artigo de `outputs/*.md` em um post Hugo dentro de `content/posts/`. |
| `make schedule` (`python3 scheduler.py`) | **O bot diário** — pesquisa tópicos, escreve, revisa e publica localmente. Ver seção abaixo. |

### O bot diário (`scheduler.py`)

É o script pensado para rodar sozinho, uma vez por dia, via cron. A cada execução:

1. **Repõe tópicos**: para qualquer categoria (`topics/<categoria>.txt`) com menos de 3 temas ainda não usados, chama `topic_researcher.py` para pesquisar mais via LLM antes de sortear — assim as listas de tópicos nunca ficam vazias.
2. **Escolhe e escreve**: sorteia um tema ainda não usado (comparando com `topics/.usados.json`, que registra todo tema que já virou artigo) e gera o artigo com `writer.py`.
3. **Revisa**: roda `proofreader.py` sobre o artigo gerado. Se o `score` retornado vier abaixo de 6/10, o artigo **não é publicado** — fica em `outputs/` para você ajustar manualmente (`make rewrite`). O tema segue marcado como usado, então a próxima execução tenta um tema diferente.
4. **Publica localmente**: se aprovado na revisão, converte o artigo em post Hugo (`post_writer.py`) em `content/posts/` e faz `git commit` (só local — **não** dá `git push`).

Ou seja: o bot roda e commita sozinho todo santo dia, mas publicar de fato no site (`git push` para a `master`, que o Cloudflare Pages builda e publica automaticamente) continua sendo uma decisão manual sua — dá pra revisar o que foi commitado antes de subir.

Categorias de tópicos hoje: `cafe_geral`, `curiosidades`, `equipamentos`, `metodos`, `receitas`. Para criar uma categoria nova, basta adicionar um arquivo `topics/<nome-da-categoria>.txt` com um tópico por linha (ou deixar vazio e rodar `make research-topics` para popular via LLM).

### Configurando o cronjob

1. Confirme o caminho do repositório e do Python/venv que você vai usar:

   ```bash
   cd /caminho/para/cafecom.georgemoura.com.br/contentgenerator
   python3 -m venv venv        # se ainda não existir
   source venv/bin/activate
   pip install -r requirements.txt
   which python3                # anote esse caminho completo
   ```

2. Edite o crontab do usuário:

   ```bash
   crontab -e
   ```

3. Adicione uma linha rodando o bot 1x por dia (exemplo às 9h da manhã), com `cd` para dentro de `contentgenerator/` e usando o Python do venv:

   ```cron
   0 9 * * * cd /caminho/para/cafecom.georgemoura.com.br/contentgenerator && /caminho/para/cafecom.georgemoura.com.br/contentgenerator/venv/bin/python scheduler.py >> logs.txt 2>&1
   ```

   - O `cd` precisa cair dentro de `contentgenerator/`, pois os scripts leem/escrevem caminhos relativos (`prompts/`, `outputs/`, `topics/`). O `git add`/`git commit` do post gerado é feito a partir da raiz do repositório automaticamente pelo próprio `scheduler.py`.
   - `logs.txt` guarda a saída de cada execução — vale checar de vez em quando para acompanhar o que foi gerado ou se algum artigo foi reprovado na revisão.

4. Salve e confira que a tarefa foi registrada:

   ```bash
   crontab -l
   ```

5. Rotina recomendada: de tempos em tempos, rode `git log` em `contentgenerator/` e `content/posts/` pra ver o que o bot commitou, dê uma lida nos posts novos e, quando estiver satisfeito, `git push` para a `master` — o Cloudflare Pages cuida do resto.

### Como funciona o controle de temas repetidos

- `topics/<categoria>.txt` é a lista mestra de temas por categoria.
- `topics/.usados.json` é o registro (gerado automaticamente, e commitado no git) de quais temas já viraram artigo, com data e arquivo gerado.
- `scheduler.py` só sorteia temas que ainda não estão em `.usados.json`. Ao gerar um artigo com sucesso, o tema é marcado como usado.
- `topic_researcher.py` pesquisa tópicos novos via LLM, comparando (sem diferenciar acento/maiúscula) com o que já existe na categoria e com o que já foi usado, para nunca repetir ou gerar algo parecido demais.

## Monetização (AdSense)

- Client ID e slots de anúncio já configurados em `config.toml` (`[params.ads]`) e renderizados pelos partials em `layouts/partials/google/`.
- `static/ads.txt` precisa continuar existindo e com o publisher ID correto — sem ele, o Google pode limitar ou não servir os anúncios.
- Google Analytics configurado via `googleAnalytics` em `config.toml`.
