import os
import re
from datetime import datetime

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), 'outputs')
POSTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../content/posts'))

def extract_title_and_content(md_text):
	# Tenta extrair o título entre **Título:** ou similar
	match = re.search(r'\*\*T[íi]tulo:?\*\*\s*(.*)', md_text)
	title = match.group(1).strip() if match else 'Post sem título'
	# Remove a linha do título do conteúdo
	content = re.sub(r'\*\*T[íi]tulo:?\*\*.*\n?', '', md_text, count=1)
	return title, content.strip()

def extract_description(md_text):
	match = re.search(r'\*\*Palavras-chave naturais:?\*\*\s*(.*?)(\n|$)', md_text)
	if match:
		return match.group(1).strip()
	return ''

def extract_keywords(md_text):
	# Procura tudo após o marcador até o próximo bloco ou fim do texto
	match = re.search(r'\*\*Palavras-chave SEO \(3\):\*\*\s*([\s\S]+?)(\n\*\*|$)', md_text)
	if match:
		block = match.group(1)
		# Extrai todas as linhas numeradas
		keywords = re.findall(r'\d+\.\s*(.*)', block)
		return [kw.strip() for kw in keywords if kw.strip()]
	return []

def convert_to_hugo_post(md_file):
	with open(md_file, 'r', encoding='utf-8') as f:
		md_text = f.read()
	title, content = extract_title_and_content(md_text)
	description = extract_description(md_text)
	keywords = extract_keywords(md_text)
	# Remove as seções de description e keywords do conteúdo
	content = re.sub(r'\*\*Palavras-chave naturais:?\*\*[\s\S]*?(\n\*\*|$)', '', content)
	content = re.sub(r'\*\*Palavras-chave SEO \(3\):\*\*[\s\S]+', '', content)
	content = re.sub(r'Palavras-chave SEO \(3\):\*\*[\s\S]+', '', content)
	content = content.strip()
	# Data do arquivo pelo nome (ex: 20251015_193101_nome.md)
	basename = os.path.basename(md_file)
	date_match = re.match(r'(\d{8})_(\d{6})', basename)
	if date_match:
		date_str = f"{date_match.group(1)}{date_match.group(2)}"
		dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
		hugo_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
	else:
		hugo_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
	# Nome do arquivo destino
	slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
	dest_file = os.path.join(POSTS_DIR, f"{slug}.md")
	# Monta o front matter novo
	keywords_str = ', '.join(f'{kw}' for kw in keywords)
	front_matter = (
		f"---\n"
		f"title: \"{title}\"\n"
		f"date: {hugo_date}\n"
		f"description: {description}\n"
		f"keywords: \"{keywords_str}\"\n"
		f"draft: false\n"
		f"---\n\n"
	)
	with open(dest_file, 'w', encoding='utf-8') as f:
		f.write(front_matter + content)
	print(f"✅ Post criado: {dest_file}")

def main():
	file_name = input("Digite o nome do arquivo do artigo (ex: 20251013_os-segredos-do-cafe.md): ")
	md_file = os.path.join(OUTPUTS_DIR, file_name)
	if not os.path.isfile(md_file):
		print(f"Arquivo não encontrado: {md_file}")
		return
	convert_to_hugo_post(md_file)

if __name__ == "__main__":
	main()
