"""ui.py

Responsabilidade:
    Reunir funcoes de apresentacao e mensagens no terminal.

Dependencias:
    - os
    - validacao

Funcoes publicas:
    - limpar_ecra
    - aguardar_enter
    - mostrar_titulo
    - mostrar_regras
    - mostrar_mensagem_erro
    - mostrar_resumo
"""

import os

from validacao import terminar_se_comando_saida


def limpar_ecra():
    """Limpa o ecrã da consola de forma portavel.

    Returns:
        None
    """
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def aguardar_enter(mensagem="Pressiona Enter para continuar..."):
    """Pausa o fluxo ate o utilizador carregar Enter.

    Args:
        mensagem (str): Texto apresentado ao utilizador.

    Returns:
        None
    """
    texto = input(mensagem)
    terminar_se_comando_saida(texto)


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
    print("3) Cada partida tem 10 perguntas.")
    print("4) Tens 20 segundos por pergunta.")
    print("5) A pontuacao por dificuldade esta sempre ativa (1/2/3).")
    print("6) No fim, recebes resumo de pontuacao e podes voltar a jogar.")
    print("7) Podes escrever 'sair' (ou '0') em qualquer input para terminar.")


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
