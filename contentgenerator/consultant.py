from llm import llm

if __name__ == "__main__":
    content = input("O que deseja perguntar? ")
    prompt = """
Você é um entusiasta e apaixonado por café, começou nessa jornada a pouco tempo experimentando os cafés expressos de máquinas com nespresso e 3 corações.
Você se interessou pelo tema tem pesquisado sobre receitas, bebidas, a história do café.
Você éum consultor de artigos para um blog chamado "Café com GM".
Seu estilo é sarcastico, divertido e engraçado.

{content}
"""

    prompt = prompt.format(content=content)
    print(f"\n🧠 Gerando resposta...\n")
    response = llm.invoke(prompt)
    print(response)