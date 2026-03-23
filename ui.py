"""ui.py

Responsabilidade:
    Reunir funcoes de apresentacao e mensagens no terminal.

Dependencias:
    Nenhuma.

Funcoes publicas:
    - mostrar_titulo
    - mostrar_regras
    - mostrar_mensagem_erro
    - mostrar_resumo
"""


def mostrar_titulo():
    """Mostra titulo principal da aplicacao.

    Returns:
        None
    """
    print("\n=== QUIZ PYTHON ===")


def mostrar_regras():
    """Mostra regras base do jogo.

    Returns:
        None
    """
    print("\nRegras / Ajuda")
    print("1) Escolhe uma opcao numerica no menu.")
    print("2) Durante o jogo, responde com o numero da opcao correta.")
    print("3) No fim, recebe resumo de pontuacao e podes voltar a jogar.")
    print("4) Podes escrever 'sair' (ou '0') em qualquer input para terminar.")


def mostrar_mensagem_erro(texto):
    """Mostra mensagem de erro consistente.

    Args:
        texto (str): Mensagem de erro.

    Returns:
        None
    """
    print(f"[ERRO] {texto}")


def mostrar_resumo(resultado):
    """Mostra resumo final de uma sessao.

    Args:
        resultado (dict): Dicionario com pontos, certas, erradas e percentagem.

    Returns:
        None
    """
    print("\nResumo final")
    print(f"Pontos: {resultado.get('pontos', 0)}")
    print(f"Certas: {resultado.get('certas', 0)}")
    print(f"Erradas: {resultado.get('erradas', 0)}")
    print(f"Percentagem: {resultado.get('percentagem', 0.0)}%")
