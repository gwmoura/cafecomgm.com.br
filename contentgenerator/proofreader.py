import os
from llm import llm
from helpers import loading_animation

def revisar_artigo(nome_arquivo):
    caminho_entrada = f"outputs/{nome_arquivo}"
    caminho_saida = f"revisions/revisao-{nome_arquivo}.json"

    if not os.path.exists(caminho_entrada):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        texto = f.read()

    with open("prompts/revision_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(texto=texto)
    print(f"\n🔍 Revisando artigo {nome_arquivo}...\n")

    resposta = llm.invoke(prompt)
    os.makedirs("revisions", exist_ok=True)

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(resposta)

    print(f"✅ Revisão salva em: {caminho_saida}")


if __name__ == "__main__":
    nome_arquivo = input("Digite o nome do arquivo do artigo (ex: 20251013_os-segredos-do-cafe.md): ")
    revisar_artigo(nome_arquivo)
