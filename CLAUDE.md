# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This repo has two parts that work together:

1. A **Hugo static site** (root) for the blog "Café com GM" (`cafecom.georgemoura.com.br`), a Portuguese-language blog about coffee.
2. **`contentgenerator/`** — a standalone Python toolset that uses an LLM (via LangChain, Ollama or OpenAI) to write, rewrite, and proofread blog articles, then converts them into Hugo posts.

## Hugo site (root)

- Config: [config.toml](config.toml). Active theme is `story` (`themes/story`); `themes/hugo-theme-flat` also exists but is disabled (commented out in config).
- Content lives in `content/posts/*.md` with standard Hugo front matter (`title`, `date`, `description`, `keywords`, `draft`).
- `layouts/` only contains overrides on top of the theme: `layouts/_default/baseof.html` and partials for Google Analytics/AdSense (`layouts/partials/google/`).
- `public/` is the built site output; `resources/_gen` is Hugo's generated resource cache. Both are build artifacts, not source.
- Deployment target is a GCS bucket (`gs://cafecom.georgemoura.com.br`), configured under `[deployment]` in config.toml.
- `static/ads.txt` declares the AdSense publisher ID (`pub-7444396631758040`) — required by Google for the site to serve ads; keep it in sync with `params.ads.client` in config.toml if the AdSense account ever changes.

Common commands:
```bash
hugo server -D          # local dev server, including drafts
hugo                    # build the static site into public/
make deploy             # build + hugo deploy (publishes public/ to the GCS bucket)
```

## contentgenerator/ (Python article pipeline)

Standalone scripts (no shared CLI entrypoint — each file is run directly with `python3 <file>.py` and prompts for input interactively). Working directory must be `contentgenerator/` since paths (`prompts/`, `outputs/`, `revisions/`, `topics/`) are relative.

```bash
cd contentgenerator
python3 writer.py       # generate a new article from a topic (make write)
python3 rewriter.py     # regenerate an existing draft in outputs/ with requested changes (make rewrite)
python3 proofreader.py  # review/proofread an article, saving JSON feedback to revisions/ (make revise)
python3 consultant.py   # freeform Q&A with the "coffee enthusiast" persona (make consultant)
python3 scheduler.py    # pick an unused topic from topics/*.txt and generate a post (used by cron)
python3 topic_researcher.py  # use the LLM to research new topics and append them to topics/*.txt (make research-topics)
python3 post_writer.py  # convert a generated outputs/*.md article into a Hugo post in content/posts/
```

Dependencies: `pip install -r requirements.txt` (langchain, langchain-ollama, langchain-openai, markdown2, python-dotenv, requests).

### Architecture

- **`llm.py`** is the single LLM entrypoint all scripts import (`from llm import llm`). It reads `.env` (`python-dotenv`) and switches between backends based on the `LLM` env var:
  - `LLM=ollama` (default): uses `langchain_ollama.OllamaLLM` against `OLLAMA_BASE_URL` (default `http://localhost:11434`) with `OLLAMA_MODEL` (default `llama3`).
  - any other value: uses `langchain_openai.ChatOpenAI` with `OPENAI_MODEL` (default `o4-mini`) and `OPENAI_API_KEY`.
  - `LLMWrapper.invoke()` normalizes both backends to return a plain string.
- **Prompts** live in `prompts/*.txt` as `.format()` templates (e.g. `article_prompt.txt` takes `{topic}`/`{description}`, `article_rewrite_prompt.txt` takes `{article}`/`{changes}`, `revision_prompt.txt` takes `{texto}`). Scripts load these at runtime — editing prompt wording is the primary way to change article style/output format.
- **Article generation flow**: `writer.py` renders `article_prompt.txt`, calls the LLM, and writes the raw markdown response to `outputs/<timestamp>_<slug>.md`. The expected article format includes `**Título:**`, `**Palavras-chave naturais:**`, and `**Palavras-chave SEO (3):**` sections — `post_writer.py` parses these markers via regex to build Hugo front matter, so prompt changes that alter these markers will break `post_writer.py`'s extraction.
- **`post_writer.py`** converts an `outputs/*.md` file into `content/posts/<slug>.md`: extracts title/description/keywords from the marker sections above, strips them from the body, derives the Hugo date from the filename's `YYYYMMDD_HHMMSS` prefix, and writes standard Hugo front matter.
- **`scheduler.py`** is the unattended daily entrypoint (see `README.md` for the cronjob). Each run: (1) tops up any category with fewer than 3 unused topics via `topic_researcher.pesquisar_novos_temas()`; (2) picks a random unused topic from `topics/*.txt` (each file name is a category — `cafe_geral`, `curiosidades`, `equipamentos`, `metodos`, `receitas`) and calls `writer.generate_article()`; (3) runs `proofreader.revisar_artigo()` as a quality gate — if the returned JSON `score` is below 6/10, the article is left in `outputs/` for manual fixup (`make rewrite`) and nothing is published; (4) otherwise converts it to a Hugo post via `post_writer.convert_to_hugo_post()` and runs `git add`/`git commit` from the repo root. It deliberately does **not** `git push` or run `hugo deploy` — going live is a manual step (`git push && make deploy`) so a human reviews content before it's public.
- **`topics_tracker.py`** is the source of truth for topic de-duplication: `topics/.usados.json` (committed, not gitignored) records every topic that has already produced an article (topic text, category, timestamp, output file). `temas_disponiveis(categoria)` filters a category's topics against that registry; `registrar_uso()` appends to it after a successful generation; `adicionar_temas()` appends new topics to a `topics/<categoria>.txt` file while skipping anything that already exists there or in the registry (comparison is accent/case-insensitive via `normalizar()`).
- **`topic_researcher.py`** renders `prompts/topic_research_prompt.txt` with a category's existing topics, asks the LLM for new ones, and appends the unique results via `topics_tracker.adicionar_temas()`. Runs standalone (`make research-topics`, prompts for a category or `todas`) or is invoked automatically by `scheduler.py` when a category is exhausted.
- `helpers.py` has small shared utilities: `slugify_topic()` (accent-stripping slug generation, also used by `post_writer.py`'s output filenames) and `loading_animation()` (CLI spinner shown while waiting on LLM calls).
- `outputs/*.md` and `revisions/*.md` are gitignored generated artifacts (raw LLM output and proofreading feedback JSON), not source content.
