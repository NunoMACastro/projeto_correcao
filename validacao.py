"""validacao.py

Responsabilidade:
    Centralizar validacao robusta de input de consola.

Dependencias:
    Nenhuma.

Contratos de entrada/saida:
    - Funcoes recebem prompts/limites e devolvem valores validados.
    - Comandos globais de saida (`sair`, `0`, etc.) terminam aplicacao.

Funcoes publicas:
    - construir_prompt_com_saida
    - terminar_se_comando_saida
    - pedir_inteiro_intervalo
    - pedir_confirmacao
    - pedir_nickname
"""


def construir_prompt_com_saida(prompt):
    """Constroi prompt com instrucao padrao de saida.

    Args:
        prompt (str): Prompt base.

    Returns:
        str: Prompt enriquecido com dica de saida.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    texto = str(prompt).strip()
    if texto.endswith(":"):
        texto = texto[:-1].strip()
    return f"{texto} (ou escreve 'sair' ou '0'): "


def terminar_se_comando_saida(texto):
    """Termina aplicacao se texto corresponder a comando de saida.

    Args:
        texto (str | None): Texto introduzido pelo utilizador.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede encerramento da app.

    Side Effects:
        - Escreve aviso de encerramento no terminal.
    """
    if texto is None:
        return

    comando = str(texto).strip().lower()
    if comando in ("sair", "exit", "quit", "q", "0"):
        print("A terminar aplicacao por comando do utilizador.")
        raise SystemExit(0)


def pedir_inteiro_intervalo(prompt, minimo, maximo):
    """Pede inteiro dentro de intervalo fechado [minimo, maximo].

    Args:
        prompt (str): Texto do input.
        minimo (int): Limite inferior permitido.
        maximo (int): Limite superior permitido.

    Returns:
        int: Valor valido no intervalo pedido.

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input do terminal.
        - Escreve mensagens de validacao no terminal.
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
        if valor < int(minimo) or valor > int(maximo):
            print(f"Valor fora do intervalo ({minimo}-{maximo}).")
            continue
        return valor


def pedir_confirmacao(prompt):
    """Pede confirmacao do tipo sim/nao.

    Args:
        prompt (str): Texto da pergunta.

    Returns:
        bool: True para sim, False para nao.

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input do terminal.
        - Escreve mensagens de validacao no terminal.
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
    """Pede nickname nao vazio e dentro dos limites configurados.

    Args:
        minimo (int): Tamanho minimo permitido.
        maximo (int): Tamanho maximo permitido.

    Returns:
        str: Nickname valido.

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input do terminal.
        - Escreve mensagens de validacao no terminal.
    """
    while True:
        nome = input(construir_prompt_com_saida("Nickname: ")).strip()
        terminar_se_comando_saida(nome)

        tamanho = len(nome)
        if tamanho < int(minimo) or tamanho > int(maximo):
            print(f"Nickname deve ter entre {minimo} e {maximo} caracteres.")
            continue
        return nome
