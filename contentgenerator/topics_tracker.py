import json
import os
import re
import unicodedata
from datetime import datetime

TOPICS_DIR = os.path.join(os.path.dirname(__file__), "topics")
USADOS_FILE = os.path.join(TOPICS_DIR, ".usados.json")


def normalizar(tema: str) -> str:
    tema = unicodedata.normalize("NFKD", tema)
    tema = tema.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", tema).strip().lower()


def listar_categorias() -> list:
    return sorted(f[:-4] for f in os.listdir(TOPICS_DIR) if f.endswith(".txt"))


def carregar_temas(categoria: str) -> list:
    caminho = os.path.join(TOPICS_DIR, f"{categoria}.txt")
    if not os.path.isfile(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def carregar_usados() -> list:
    if not os.path.isfile(USADOS_FILE):
        return []
    with open(USADOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def temas_usados_normalizados() -> set:
    return {normalizar(item["tema"]) for item in carregar_usados()}


def temas_disponiveis(categoria: str) -> list:
    usados = temas_usados_normalizados()
    return [t for t in carregar_temas(categoria) if normalizar(t) not in usados]


def registrar_uso(tema: str, categoria: str, arquivo: str, slug: str) -> None:
    usados = carregar_usados()
    usados.append(
        {
            "tema": tema,
            "categoria": categoria,
            "data": datetime.now().isoformat(timespec="seconds"),
            "arquivo": arquivo,
            "url": '/posts/' + slug,
            "slug": slug,
        }
    )
    with open(USADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usados, f, ensure_ascii=False, indent=2)
        f.write("\n")


def adicionar_temas(categoria: str, novos_temas: list) -> list:
    """Acrescenta temas novos ao arquivo da categoria, ignorando os que já existem ou já foram usados."""
    existentes_normalizados = {normalizar(t) for t in carregar_temas(categoria)}
    usados = temas_usados_normalizados()
    caminho = os.path.join(TOPICS_DIR, f"{categoria}.txt")

    precisa_newline = os.path.isfile(caminho) and os.path.getsize(caminho) > 0
    if precisa_newline:
        with open(caminho, "rb") as f:
            f.seek(-1, os.SEEK_END)
            precisa_newline = f.read(1) != b"\n"

    adicionados = []
    with open(caminho, "a", encoding="utf-8") as f:
        if precisa_newline:
            f.write("\n")
        for tema in novos_temas:
            tema = tema.strip()
            if not tema:
                continue
            norm = normalizar(tema)
            if norm in existentes_normalizados or norm in usados:
                continue
            f.write(tema + "\n")
            existentes_normalizados.add(norm)
            adicionados.append(tema)
    return adicionados
