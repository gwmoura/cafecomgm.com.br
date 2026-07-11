#### cronjob

0 9 * * * cd /caminho/para/cafe-blog-ai && /caminho/para/venv/bin/python scheduler.py >> logs.txt 2>&1

#### Como funciona o controle de temas repetidos

- `topics/<categoria>.txt` continua sendo a lista mestra de temas por categoria.
- `topics/.usados.json` é o registro (gerado automaticamente) de quais temas já viraram artigo, com data e arquivo gerado.
- `scheduler.py` só sorteia temas que ainda não estão em `.usados.json`. Ao gerar um artigo com sucesso, o tema é marcado como usado.
- Se todas as categorias estiverem esgotadas, o `scheduler.py` aciona `topic_researcher.py` automaticamente para pesquisar novos temas via LLM e adicioná-los ao arquivo da categoria antes de continuar.
- `topic_researcher.py` também pode ser rodado manualmente (`make research-topics`) para engordar as listas de temas sob demanda, para uma categoria específica ou para todas.
