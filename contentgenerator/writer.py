import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_ollama.llms import OllamaLLM

# carregar variáveis do .env
load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# inicializar o modelo Ollama via LangChain
llm = OllamaLLM(model=MODEL, temperature=0.7)

def generate_article(topic: str, description: str = "") -> str:
    # carregar o template do prompt
    with open("prompts/article_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(topic=topic, description=description)
    print(f"\n🧠 Gerando artigo sobre: {topic}...\n")

    # gerar texto
    response = llm.invoke(prompt)  # ou llm(prompt)

    # salvar o resultado
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{topic.lower().replace(' ', '_')}.md"

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
