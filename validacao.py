"""validacao.py

Responsabilidade:
    Fornecer funcoes de validacao robusta para entradas do utilizador.

Dependencias:
    Nenhuma.

Funcoes publicas:
    - construir_prompt_com_saida
    - terminar_se_comando_saida
    - pedir_inteiro_intervalo
    - pedir_confirmacao
    - pedir_nickname
"""


def construir_prompt_com_saida(prompt):
    """Constroi prompt com instrucoes de saida para o utilizador.

    Args:
        prompt (str): Prompt base.

    Returns:
        str: Prompt enriquecido com dica de comando de saida.
    """
    texto = prompt.strip()
    if texto.endswith(":"):
        texto = texto[:-1].strip()
    return f"{texto} (ou escreve 'sair' ou '0'): "


def terminar_se_comando_saida(texto):
    """Termina a aplicacao se o utilizador escrever um comando de saida.

    Args:
        texto (str): Conteudo introduzido pelo utilizador.

    Returns:
        None

    Raises:
        SystemExit: Quando o utilizador pede para sair da aplicacao.
    """
    if texto is None:
        return

    comando = texto.strip().lower()
    if comando in ("sair", "exit", "quit", "q", "0"):
        print("A terminar aplicacao por comando do utilizador.")
        raise SystemExit(0)


def pedir_inteiro_intervalo(prompt, minimo, maximo):
    """Pede um inteiro no intervalo [minimo, maximo].

    Args:
        prompt (str): Texto a apresentar no input.
        minimo (int): Limite inferior permitido.
        maximo (int): Limite superior permitido.

    Returns:
        int: Inteiro valido no intervalo.
    """
    while True:
        texto = input(construir_prompt_com_saida(prompt)).strip()
        terminar_se_comando_saida(texto)
        if not texto:
            print("Entrada vazia. Tenta novamente.")
            continue
        if not texto.isdigit():
            print("Entrada invalida. Introduz apenas numeros.")
            continue
        valor = int(texto)
        if valor < minimo or valor > maximo:
            print(f"Valor fora do intervalo ({minimo}-{maximo}).")
            continue
        return valor


def pedir_confirmacao(prompt):
    """Pede uma confirmacao do tipo sim/nao.

    Args:
        prompt (str): Texto da pergunta.

    Returns:
        bool: True para sim, False para nao.
    """
    while True:
        texto = input(construir_prompt_com_saida(prompt)).strip().lower()
        terminar_se_comando_saida(texto)
        if texto in ("s", "sim", "y", "yes"):
            return True
        if texto in ("n", "nao", "não", "no"):
            return False
        print("Resposta invalida. Usa 's' para sim ou 'n' para nao.")


def pedir_nickname(minimo=1, maximo=20):
    """Pede nickname nao vazio e com tamanho valido.

    Args:
        minimo (int): Tamanho minimo permitido.
        maximo (int): Tamanho maximo permitido.

    Returns:
        str: Nickname valido.
    """
    while True:
        nome = input(construir_prompt_com_saida("Nickname: ")).strip()
        terminar_se_comando_saida(nome)
        tamanho = len(nome)
        if tamanho < minimo or tamanho > maximo:
            print(f"Nickname deve ter entre {minimo} e {maximo} caracteres.")
            continue
        return nome
