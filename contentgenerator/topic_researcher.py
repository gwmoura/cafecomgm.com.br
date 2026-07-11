import re

from llm import llm
from topics_tracker import adicionar_temas, carregar_temas, listar_categorias

PROMPT_PATH = "prompts/topic_research_prompt.txt"


def pesquisar_novos_temas(categoria: str, quantidade: int = 5) -> list:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    temas_existentes = carregar_temas(categoria)
    prompt = prompt_template.format(
        categoria=categoria,
        temas_existentes="\n".join(f"- {t}" for t in temas_existentes) or "(nenhum ainda)",
        quantidade=quantidade,
    )

    print(f"🔎 Pesquisando {quantidade} novos temas para a categoria '{categoria}'...")
    resposta = llm.invoke(prompt)
    propostos = re.findall(r"\d+[.)]\s*(.+)", resposta)
    adicionados = adicionar_temas(categoria, propostos)

    if adicionados:
        print(f"✅ {len(adicionados)} novos temas adicionados a topics/{categoria}.txt:")
        for tema in adicionados:
            print(f"   - {tema}")
    else:
        print(f"⚠️ Nenhum tema novo e único foi encontrado para '{categoria}'.")
    return adicionados


def pesquisar_para_todas_categorias(quantidade: int = 5) -> dict:
    return {categoria: pesquisar_novos_temas(categoria, quantidade) for categoria in listar_categorias()}


if __name__ == "__main__":
    categorias = listar_categorias()
    print("Categorias disponíveis:", ", ".join(categorias))
    escolha = input("Digite a categoria (ou 'todas' para pesquisar em todas): ").strip()
    quantidade_str = input("Quantos temas gerar por categoria? [5]: ").strip()
    quantidade = int(quantidade_str) if quantidade_str else 5

    if escolha.lower() == "todas":
        pesquisar_para_todas_categorias(quantidade)
    elif escolha in categorias:
        pesquisar_novos_temas(escolha, quantidade)
    else:
        print(f"Categoria '{escolha}' não encontrada.")
