import os
import random
import subprocess
from datetime import datetime

TOPIC_DIR = "topics"

def escolher_tema():
    arquivos = [os.path.join(TOPIC_DIR, f) for f in os.listdir(TOPIC_DIR) if f.endswith(".txt")]
    arquivo_escolhido = random.choice(arquivos)

    with open(arquivo_escolhido, "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    tema = random.choice(linhas)
    categoria = os.path.basename(arquivo_escolhido).replace(".txt", "")
    print(f"Tema escolhido: {tema} (categoria: {categoria})")
    return tema

def gerar_artigo(tema):
    comando = ["python", "main.py"]
    processo = subprocess.Popen(comando, stdin=subprocess.PIPE, text=True)
    processo.communicate(input=tema)

if __name__ == "__main__":
    tema = escolher_tema()
    gerar_artigo(tema)
    print(f"✅ Artigo gerado com sucesso ({datetime.now().strftime('%d/%m/%Y %H:%M')})")
