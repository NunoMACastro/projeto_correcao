"""app_service.py

Responsabilidade:
    Coordenar bootstrap da app e dispatch do menu principal.

Dependencias:
    - campeonato_flow
    - config
    - jogo_flow
    - log_service
    - menu
    - perguntas_service
    - pontuacoes_service
    - ui

Contratos de entrada/saida:
    - carregar_contexto_aplicacao(): carrega perguntas válidas e relatório de carga.
    - processar_opcao_menu(...): encaminha opção do menu para o fluxo respetivo.
    - ciclo_menu_principal(...): mantém ciclo principal de navegação.
    - executar_aplicacao(): arranca app, trata bootstrap e encerramento.

Funcoes publicas:
    - carregar_contexto_aplicacao
    - processar_opcao_menu
    - ciclo_menu_principal
    - executar_aplicacao
"""

from campeonato_flow import executar_fluxo_campeonato
from config import MENU_PRINCIPAL_OPCOES
from jogo_flow import executar_fluxo_jogo
from log_service import registrar_evento
from menu import ler_opcao_menu, mostrar_menu_principal
from perguntas_service import carregar_perguntas_com_relatorio
from pontuacoes_service import mostrar_top10
from ui import aguardar_enter, iniciar_ecra, mostrar_mensagem_aviso, mostrar_mensagem_erro, mostrar_regras


def carregar_contexto_aplicacao():
    """Carrega dados base e constrói contexto inicial da aplicação.

    Args:
        Nenhum.

    Returns:
        dict: Contexto com perguntas válidas e metadados de carga.

    Raises:
        FileNotFoundError: Quando ficheiro de perguntas não existe.
        ValueError: Quando não existem perguntas válidas suficientes.

    Side Effects:
        - Lê ficheiro de perguntas.
        - Regista eventos de observabilidade no ficheiro de logs.
    """
    relatorio = carregar_perguntas_com_relatorio()

    for invalida in relatorio.get("invalidas", []):
        registrar_evento("WARNING", "pergunta_invalida_ignorada", invalida)

    registrar_evento(
        "INFO",
        "carga_perguntas_concluida",
        {
            "total": relatorio.get("total", 0),
            "validas": len(relatorio.get("validas", [])),
            "invalidas": len(relatorio.get("invalidas", [])),
        },
    )

    return {
        "perguntas": relatorio.get("validas", []),
        "relatorio_perguntas": relatorio,
    }


def processar_opcao_menu(opcao, contexto_app):
    """Processa opção selecionada no menu principal.

    Args:
        opcao (int): Opção numérica escolhida.
        contexto_app (dict): Contexto global da aplicação.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Encaminha para fluxos que fazem I/O de consola e/ou ficheiro.
    """
    if opcao == 1:
        executar_fluxo_jogo(contexto_app)
    elif opcao == 2:
        iniciar_ecra("Regras / Ajuda")
        mostrar_regras()
        aguardar_enter("Pressiona Enter para voltar ao menu... ")
    elif opcao == 3:
        iniciar_ecra("Top 10")
        try:
            mostrar_top10()
        except (ValueError, OSError) as erro:
            registrar_evento("ERROR", "erro_mostrar_top10", {"erro": str(erro)})
            mostrar_mensagem_erro("Não foi possível carregar o Top 10.")
        aguardar_enter("Pressiona Enter para voltar ao menu... ")
    elif opcao == 4:
        executar_fluxo_campeonato(contexto_app)


def ciclo_menu_principal(contexto_app):
    """Executa ciclo principal do menu até encerramento da app.

    Args:
        contexto_app (dict): Contexto global da aplicação.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Lê input e escreve no terminal.
    """
    perguntas = contexto_app["perguntas"]

    while True:
        iniciar_ecra("Menu Principal")
        print(f"Perguntas carregadas: {len(perguntas)}")
        mostrar_menu_principal(MENU_PRINCIPAL_OPCOES)
        opcao = ler_opcao_menu(1, len(MENU_PRINCIPAL_OPCOES))
        processar_opcao_menu(opcao, contexto_app)


def executar_aplicacao():
    """Arranca aplicação com bootstrap e observabilidade.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saída por comando global.

    Side Effects:
        - Lê ficheiros JSON de dados.
        - Escreve ficheiro JSON de logs.
        - Escreve no terminal.
    """
    registrar_evento("INFO", "app_inicio", {"componente": "quiz_python"})

    try:
        contexto = carregar_contexto_aplicacao()
    except (FileNotFoundError, ValueError) as erro:
        registrar_evento("ERROR", "bootstrap_falhou", {"erro": str(erro)})
        iniciar_ecra("Erro de arranque")
        mostrar_mensagem_erro(str(erro))
        return

    invalidas = len(contexto["relatorio_perguntas"].get("invalidas", []))
    if invalidas:
        iniciar_ecra("Arranque")
        mostrar_mensagem_aviso(
            f"Foram ignoradas {invalidas} perguntas inválidas durante a carga."
        )
        aguardar_enter("Pressiona Enter para continuar para o menu... ")

    try:
        ciclo_menu_principal(contexto)
    finally:
        registrar_evento("INFO", "app_fim", {"motivo": "encerramento"})
