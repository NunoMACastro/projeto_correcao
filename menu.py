"""menu.py

Responsabilidade:
    Apresentar menu principal e ler opcao valida.

Dependencias:
    - validacao

Contratos de entrada/saida:
    - mostrar_menu_principal(opcoes): imprime opcoes.
    - ler_opcao_menu(min_opcao, max_opcao): devolve inteiro valido no intervalo.

Funcoes publicas:
    - mostrar_menu_principal
    - ler_opcao_menu
"""

from validacao import pedir_inteiro_intervalo


def mostrar_menu_principal(opcoes):
    """Mostra opcoes do menu principal.

    Args:
        opcoes (list[tuple[str, str]]): Lista de pares (codigo, descricao).

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    for codigo, descricao in opcoes:
        print(f"{codigo}) {descricao}")


def ler_opcao_menu(min_opcao, max_opcao):
    """Le escolha numerica valida para menu.

    Args:
        min_opcao (int): Menor opcao permitida.
        max_opcao (int): Maior opcao permitida.

    Returns:
        int: Opcao escolhida.

    Raises:
        SystemExit: Quando utilizador pede saida em input.

    Side Effects:
        - Le input do terminal.
    """
    return pedir_inteiro_intervalo("Escolha uma opção: ", min_opcao, max_opcao)
