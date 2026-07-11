import random
from datetime import datetime

from topic_researcher import pesquisar_novos_temas
from topics_tracker import listar_categorias, registrar_uso, temas_disponiveis
from writer import generate_article


def escolher_tema():
    categorias = listar_categorias()
    random.shuffle(categorias)

    for categoria in categorias:
        disponiveis = temas_disponiveis(categoria)
        if disponiveis:
            tema = random.choice(disponiveis)
            print(f"Tema escolhido: {tema} (categoria: {categoria})")
            return tema, categoria

    print("⚠️ Todos os temas cadastrados já foram usados. Pesquisando novos temas...")
    categoria = random.choice(categorias)
    novos = pesquisar_novos_temas(categoria, quantidade=5)
    if not novos:
        raise RuntimeError(
            "Não foi possível encontrar novos temas automaticamente. "
            "Adicione temas manualmente em topics/ ou rode topic_researcher.py."
        )

    tema = random.choice(novos)
    print(f"Tema escolhido: {tema} (categoria: {categoria})")
    return tema, categoria


def gerar_artigo(tema: str, categoria: str) -> str:
    _, arquivo = generate_article(tema)
    registrar_uso(tema, categoria, arquivo)
    return arquivo

if __name__ == "__main__":
    tema, categoria = escolher_tema()
    gerar_artigo(tema, categoria)
    print(f"✅ Artigo gerado com sucesso ({datetime.now().strftime('%d/%m/%Y %H:%M')})")
