import json
import os
import random
import re
import subprocess
from datetime import datetime

from post_writer import convert_to_hugo_post
from proofreader import revisar_artigo
from topic_researcher import pesquisar_novos_temas
from topics_tracker import listar_categorias, registrar_uso, temas_disponiveis
from writer import generate_article

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MIN_TEMAS_DISPONIVEIS = 3  # abaixo disso, a categoria é reabastecida antes de sortear
SCORE_MINIMO_PUBLICACAO = 6  # score do proofreader (0-10) abaixo do qual o post não é publicado


def repor_temas_esgotando():
    """Pesquisa novos temas via LLM para categorias que estão prestes a esgotar."""
    for categoria in listar_categorias():
        disponiveis = temas_disponiveis(categoria)
        if len(disponiveis) < MIN_TEMAS_DISPONIVEIS:
            print(f"📋 Categoria '{categoria}' com {len(disponiveis)} tema(s) livre(s). Pesquisando mais...")
            pesquisar_novos_temas(categoria, quantidade=5)


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


def extrair_score(revisao_texto):
    if not revisao_texto:
        return None
    try:
        return json.loads(revisao_texto).get("score")
    except json.JSONDecodeError:
        match = re.search(r'"score"\s*:\s*([\d.]+)', revisao_texto)
        return float(match.group(1)) if match else None


def revisar_e_publicar(arquivo: str, tema: str, categoria: str) -> bool:
    """Roda o proofreader como gate de qualidade e, se aprovado, converte o
    artigo em post Hugo e commita localmente (sem git push nem deploy)."""
    basename = os.path.basename(arquivo)
    revisao = revisar_artigo(basename)
    score = extrair_score(revisao)

    if score is not None and score < SCORE_MINIMO_PUBLICACAO:
        print(
            f"⚠️ Revisão reprovou o artigo (score {score}/10). "
            f"Mantido em {arquivo} para ajuste manual (make rewrite)."
        )
        return False

    convert_to_hugo_post(arquivo)

    try:
        subprocess.run(
            ["git", "add", "content/posts", "contentgenerator/topics"],
            cwd=REPO_ROOT,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f'content: novo post sobre "{tema}" ({categoria})'],
            cwd=REPO_ROOT,
            check=True,
        )
        print(
            "✅ Post commitado localmente. Revise e rode 'git push' quando quiser publicar "
            "(o Cloudflare Pages builda e publica automaticamente ao atualizar a master)."
        )
    except subprocess.CalledProcessError as erro:
        print(f"⚠️ Não foi possível commitar automaticamente: {erro}")

    return True


if __name__ == "__main__":
    repor_temas_esgotando()
    tema, categoria = escolher_tema()
    arquivo = gerar_artigo(tema, categoria)
    revisar_e_publicar(arquivo, tema, categoria)
    print(f"✅ Execução concluída ({datetime.now().strftime('%d/%m/%Y %H:%M')})")
