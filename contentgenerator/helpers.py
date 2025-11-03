import time
import unicodedata
import re

def loading_animation(stop_event):
    chars = ['|', '/', '-', '\\']
    idx = 0
    print('⏳ Gerando conteúdo da IA ', end='', flush=True)
    while not stop_event.is_set():
        print(chars[idx % len(chars)], end='\r', flush=True)
        idx += 1
        time.sleep(0.2)
    print(' ' * 30, end='\r')  # Limpa linha


def slugify_topic(topic: str) -> str:
    # Normaliza unicode, remove acentos
    topic = unicodedata.normalize('NFKD', topic)
    topic = topic.encode('ascii', 'ignore').decode('ascii')
    # Substitui caracteres não alfanuméricos por hífen
    topic = re.sub(r'[^a-zA-Z0-9]+', '-', topic)
    # Remove hífens duplicados e bordas
    topic = re.sub(r'-+', '-', topic).strip('-')
    # Converte para minúsculas
    return topic.lower()