import os
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM

# carregar variáveis do .env
load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3")
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# inicializar o modelo Ollama via LangChain
llm = OllamaLLM(
    model=MODEL,
    temperature=0.7,
    base_url=BASE_URL
)