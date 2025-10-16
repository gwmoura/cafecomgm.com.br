import os
import threading
from llm import llm
from helpers import loading_animation

def regenerate_article(file_name: str, changes: str) -> str:
    caminho_entrada = f"outputs/{file_name}"

    if not os.path.exists(caminho_entrada):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        article = f.read()

    with open("prompts/article_rewrite_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(article=article, changes=changes)
    print(f"\n🧠 Gerando novamente o artigo...\n")

    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    loader_thread.start()
    response = llm.invoke(prompt)
    stop_event.set()
    loader_thread.join()

    # salvar o resultado
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{file_name}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"✅ Artigo salvo em: {filename}")
    return response


if __name__ == "__main__":
    file_name = input("Digite o nome do arquivo do artigo (ex: 20251013_os-segredos-do-cafe.md): ")
    changes = input("Digite as mudanças necessárias: ")
    article = regenerate_article(file_name, changes)
    print("\nPrévia do artigo:\n")
    print(article[:800])
