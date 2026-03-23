"""ui.py

Responsabilidade:
    Centralizar apresentacao de consola com estilo consistente.

Dependencias:
    - os
    - validacao

Contratos de entrada/saida:
    - Funcoes imprimem mensagens no terminal e nao devolvem dados de negocio.

Funcoes publicas:
    - limpar_ecra
    - mostrar_titulo
    - iniciar_ecra
    - aguardar_enter
    - mostrar_regras
    - mostrar_mensagem_erro
    - mostrar_mensagem_aviso
    - mostrar_mensagem_sucesso
    - mostrar_mensagem_info
    - mostrar_resumo
"""

import os

from validacao import terminar_se_comando_saida


def limpar_ecra():
    """Limpa o ecra da consola de forma portavel.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Executa comando `clear` (Unix) ou `cls` (Windows).
    """
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def mostrar_titulo():
    """Mostra titulo principal da aplicacao.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print("\n=== QUIZ PYTHON ===")


def iniciar_ecra(titulo_secao=""):
    """Inicializa novo ecrã com limpeza e cabecalho consistente.

    Args:
        titulo_secao (str): Titulo opcional da secao atual.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Limpa a consola.
        - Escreve titulo global e titulo da secao.
    """
    limpar_ecra()
    mostrar_titulo()
    if str(titulo_secao).strip():
        print(f"\n{titulo_secao}")


def aguardar_enter(mensagem="Pressiona Enter para continuar... "):
    """Pausa fluxo ate o utilizador carregar Enter.

    Args:
        mensagem (str): Texto apresentado ao utilizador.

    Returns:
        None

    Raises:
        SystemExit: Se utilizador escrever comando de saida.

    Side Effects:
        - Lê input do terminal.
        - Pode terminar aplicacao via validacao centralizada.
    """
    texto = input(mensagem)
    terminar_se_comando_saida(texto)


def mostrar_mensagem_erro(texto):
    """Mostra mensagem de erro com formato unificado.

    Args:
        texto (str): Conteudo da mensagem.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print(f"[ERRO] {texto}")


def mostrar_mensagem_aviso(texto):
    """Mostra aviso com formato unificado.

    Args:
        texto (str): Conteudo da mensagem.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print(f"[AVISO] {texto}")


def mostrar_mensagem_sucesso(texto):
    """Mostra mensagem de sucesso com formato unificado.

    Args:
        texto (str): Conteudo da mensagem.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print(f"[OK] {texto}")


def mostrar_mensagem_info(texto):
    """Mostra informacao neutra com formato unificado.

    Args:
        texto (str): Conteudo da mensagem.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print(f"[INFO] {texto}")


def mostrar_regras():
    """Mostra regras e ajuda do jogo.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print("\nRegras / Ajuda")
    print("1) Escolhe uma opcao numerica no menu.")
    print("2) Durante o jogo, responde com o numero da opcao correta.")
    print("3) Cada partida tem 10 perguntas aleatorias.")
    print("4) Tens 20 segundos por pergunta.")
    print("5) Pontuacao por dificuldade esta sempre ativa (1/2/3).")
    print("6) No fim, recebes resumo e podes voltar a jogar.")
    print("7) Podes escrever 'sair' (ou '0') em qualquer input para terminar.")


def mostrar_resumo(resultado):
    """Mostra resumo final de uma sessao.

    Args:
        resultado (dict): Dicionario com pontos, certas, erradas e percentagem.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve no terminal.
    """
    print("\nResumo final")
    print(f"Pontos: {resultado.get('pontos', 0)}")
    print(f"Certas: {resultado.get('certas', 0)}")
    print(f"Erradas: {resultado.get('erradas', 0)}")
    print(f"Percentagem: {resultado.get('percentagem', 0.0)}%")
