import os
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI

# carregar variáveis do .env
load_dotenv()

LLM = os.getenv("LLM", "ollama")

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")

if LLM == "ollama":
    # inicializar o modelo Ollama via LangChain
    MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    iallm = OllamaLLM(
        model=MODEL,
        temperature=0.7,
        base_url=BASE_URL
    )
else:
    # inicializar o modelo OpenAI via LangChain
    MODEL = os.getenv("OPENAI_MODEL", "o4-mini")
    iallm = ChatOpenAI(
        model=MODEL,
        # temperature=0.7,
        max_retries=2,
        api_key=OPENAI_API_KEY
    )

class LLMWrapper:
    def __init__(self, llm_instance):
        self.llm = llm_instance
        self.response = ""

    def invoke(self, prompt: str) -> str:
        self.response = self.llm.invoke(prompt)
        if not isinstance(self.response, str):
            self.response = self.response.content
        return self.response

llm = LLMWrapper(iallm)