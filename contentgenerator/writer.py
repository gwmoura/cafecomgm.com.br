import os
import threading
import time
from datetime import datetime
from llm import llm
from helpers import loading_animation, slugify_topic

def generate_article(topic: str, description: str = "") -> str:
    # carregar o template do prompt
    with open("prompts/article_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(topic=topic, description=description)
    print(f"\n🧠 Gerando artigo sobre: {topic}...\n")

    # mostrar loading enquanto gera texto
    stop_event = threading.Event()
    loader_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    loader_thread.start()
    response = llm.invoke(prompt)
    stop_event.set()
    loader_thread.join()

    # salvar o resultado
    os.makedirs("outputs", exist_ok=True)
    slug = slugify_topic(topic)
    filename = f"outputs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{slug}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)

    print(f"✅ Artigo salvo em: {filename}")
    return response

if __name__ == "__main__":
    topic = input("Digite o tema do artigo sobre café: ")
    description = input("Digite uma breve descrição ou pontos que gostaria de incluir (opcional): ")
    article = generate_article(topic, description)
    print("\nPrévia do artigo:\n")
    print(article[:800])
