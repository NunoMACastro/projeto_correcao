"""app_service.py

Responsabilidade:
    Orquestrar fluxos da aplicacao (menu, jogo, campeonato e bootstrap).

Dependencias:
    - time
    - campeonato_service
    - config
    - jogo_service
    - log_service
    - menu
    - perguntas_service
    - pontuacoes_service
    - ui
    - validacao

Contratos de entrada/saida:
    - executar_aplicacao(): inicia app e gere ciclo principal.
    - ciclo_menu_principal(contexto): navega opcoes do menu.

Funcoes publicas:
    - executar_aplicacao
    - ciclo_menu_principal
"""

import time

from campeonato_service import determinar_vencedor_campeonato, registar_resultado_ronda, selecionar_perguntas_ronda
from config import CONFIG_PADRAO, LIMITES, MENU_PRINCIPAL_OPCOES, NUM_PERGUNTAS_FIXAS, TEMPO_LIMITE_FIXO
from jogo_service import aplicar_avaliacao_no_estado, avaliar_resposta, finalizar_estado_sessao, iniciar_estado_sessao
from log_service import registrar_evento
from menu import ler_opcao_menu, mostrar_menu_principal
from pontuacoes_service import guardar_resultado, mostrar_top10
from perguntas_service import (
    atualizar_historico_global,
    carregar_perguntas_com_relatorio,
    filtrar_perguntas,
    listar_dificuldades,
    reiniciar_historico_se_necessario,
    selecionar_perguntas_com_historico,
)
from ui import (
    aguardar_enter,
    iniciar_ecra,
    mostrar_mensagem_aviso,
    mostrar_mensagem_erro,
    mostrar_mensagem_info,
    mostrar_mensagem_sucesso,
    mostrar_regras,
    mostrar_resumo,
)
from validacao import pedir_confirmacao, pedir_inteiro_intervalo, pedir_nickname


def escolher_filtro(rotulo, valores):
    """Permite escolher um valor de filtro, incluindo opcao `'todas'`.

    Args:
        rotulo (str): Nome legivel do filtro.
        valores (list[str]): Valores disponiveis sem `'todas'`.

    Returns:
        str: Valor escolhido.

    Raises:
        SystemExit: Quando utilizador pede saida durante input.

    Side Effects:
        - Escreve no terminal e le input do utilizador.
    """
    opcoes = ["todas"] + list(valores)
    print(f"\nEscolhe {rotulo}:")
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"{indice}) {opcao}")

    escolha = pedir_inteiro_intervalo(
        prompt="Opcao: ",
        minimo=1,
        maximo=len(opcoes),
    )
    return opcoes[escolha - 1]


def configurar_sessao_base(dificuldade):
    """Constroi configuracao fixa da sessao conforme contrato atual.

    Args:
        dificuldade (str): Dificuldade selecionada no fluxo atual.

    Returns:
        dict: Configuracao final de sessao.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    config = dict(CONFIG_PADRAO)
    config["num_perguntas"] = NUM_PERGUNTAS_FIXAS
    config["categoria"] = "todas"
    config["dificuldade"] = dificuldade
    config["modo_relogio"] = True
    config["tempo_limite"] = TEMPO_LIMITE_FIXO
    config["pontuacao_por_dificuldade"] = True
    return config


def recolher_resposta_interativa(pergunta):
    """Apresenta pergunta no terminal e recolhe resposta cronometrada.

    Args:
        pergunta (dict): Pergunta a apresentar.

    Returns:
        dict: `{"indice_resposta": int, "tempo_resposta_seg": float}`.

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Escreve pergunta/opcoes no terminal.
        - Le input do utilizador.
    """
    enunciado = pergunta.get("pergunta", "")
    opcoes = pergunta.get("opcoes", [])

    print(f"\n{enunciado}")
    for i, opcao in enumerate(opcoes, start=1):
        print(f"{i}) {opcao}")

    inicio = time.time()
    indice_resposta = pedir_inteiro_intervalo("Resposta: ", 1, len(opcoes)) - 1
    fim = time.time()

    return {
        "indice_resposta": indice_resposta,
        "tempo_resposta_seg": round(fim - inicio, 3),
    }


def mostrar_feedback_pergunta(avaliacao, pergunta):
    """Mostra feedback apos responder a uma pergunta.

    Args:
        avaliacao (dict): Resultado unitario da pergunta.
        pergunta (dict): Pergunta original.

    Returns:
        None

    Raises:
        Nenhum.

    Side Effects:
        - Escreve mensagens de feedback no terminal.
    """
    if avaliacao.get("fora_tempo", False):
        mostrar_mensagem_aviso("Tempo esgotado. Conta como errada.")
    elif avaliacao.get("correta", False):
        mostrar_mensagem_sucesso("Resposta correta.")
    else:
        mostrar_mensagem_erro("Resposta errada.")

    if pergunta.get("explicacao"):
        mostrar_mensagem_info(f"Explicacao: {pergunta.get('explicacao')}")


def executar_sessao_interativa(perguntas, config, nickname):
    """Executa sessao interativa com avaliacao de dominio separada.

    Args:
        perguntas (list[dict]): Perguntas selecionadas para sessao.
        config (dict): Configuracao da sessao.
        nickname (str): Nome do jogador.

    Returns:
        dict: Resultado consolidado da sessao.

    Raises:
        ValueError: Em inconsistencias de avaliacao.
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input e escreve feedback no terminal.
    """
    estado = iniciar_estado_sessao(perguntas, config, nickname)

    for pergunta in perguntas:
        resposta = recolher_resposta_interativa(pergunta)
        avaliacao = avaliar_resposta(
            pergunta=pergunta,
            indice_resposta=resposta["indice_resposta"],
            tempo_resposta_seg=resposta["tempo_resposta_seg"],
            config=config,
        )
        aplicar_avaliacao_no_estado(estado, pergunta, avaliacao)
        mostrar_feedback_pergunta(avaliacao, pergunta)

    return finalizar_estado_sessao(estado)


def carregar_contexto_aplicacao():
    """Carrega dados base e constroi contexto inicial da aplicacao.

    Args:
        Nenhum.

    Returns:
        dict: Contexto com perguntas validas e metadados de carga.

    Raises:
        FileNotFoundError: Quando ficheiro de perguntas nao existe.
        ValueError: Quando nao existem perguntas validas suficientes.

    Side Effects:
        - Le ficheiro de perguntas.
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


def executar_fluxo_jogo(contexto_app):
    """Executa fluxo de jogo normal com re-jogar.

    Args:
        contexto_app (dict): Contexto global da aplicacao.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input e escreve no terminal.
        - Le/escreve ficheiros JSON de historico e pontuacoes.
        - Regista eventos de observabilidade.
    """
    iniciar_ecra("Modo Jogo")
    perguntas = contexto_app["perguntas"]

    nickname = pedir_nickname(
        minimo=LIMITES["nickname_min"],
        maximo=LIMITES["nickname_max"],
    )

    dificuldades = listar_dificuldades(perguntas)

    while True:
        dificuldade = escolher_filtro("dificuldade", dificuldades)
        perguntas_filtradas = filtrar_perguntas(
            perguntas=perguntas,
            categoria="todas",
            dificuldade=dificuldade,
        )
        if len(perguntas_filtradas) < NUM_PERGUNTAS_FIXAS:
            mostrar_mensagem_erro(
                "Nao ha perguntas suficientes para jogar 10 nesta dificuldade. "
                "Escolhe outra dificuldade."
            )
            continuar = pedir_confirmacao("Queres escolher outros filtros? (s/n): ")
            if continuar:
                continue
            return

        ids_elegiveis = [str(pergunta.get("id", "")) for pergunta in perguntas_filtradas]

        try:
            ids_historico_global = reiniciar_historico_se_necessario(ids_elegiveis)
        except (ValueError, OSError) as erro:
            registrar_evento("ERROR", "erro_historico_reiniciar", {"erro": str(erro)})
            mostrar_mensagem_erro("Falha ao preparar historico de perguntas.")
            return

        print(f"\nEsta partida tera sempre {NUM_PERGUNTAS_FIXAS} perguntas.")
        print(f"Tempo por pergunta: {TEMPO_LIMITE_FIXO}s | Pontuacao por dificuldade: ativa.")

        selecionadas = selecionar_perguntas_com_historico(
            perguntas=perguntas_filtradas,
            quantidade=NUM_PERGUNTAS_FIXAS,
            ids_historico_global=ids_historico_global,
        )
        if not selecionadas:
            mostrar_mensagem_erro("Nao foi possivel selecionar perguntas.")
            return

        config_sessao = configurar_sessao_base(dificuldade)
        registrar_evento(
            "INFO",
            "sessao_inicio",
            {
                "nickname": nickname,
                "modo": "jogo",
                "dificuldade": dificuldade,
                "num_perguntas": len(selecionadas),
            },
        )

        resultado = executar_sessao_interativa(selecionadas, config_sessao, nickname)

        try:
            guardar_resultado(resultado)
            registrar_evento(
                "INFO",
                "pontuacao_guardada",
                {
                    "nickname": nickname,
                    "pontos": resultado.get("pontos", 0),
                },
            )
        except (ValueError, OSError) as erro:
            registrar_evento("ERROR", "erro_guardar_pontuacao", {"erro": str(erro)})
            mostrar_mensagem_erro("Nao foi possivel guardar pontuacao.")

        try:
            atualizar_historico_global(resultado.get("ids_usadas_sessao", []))
        except (ValueError, OSError) as erro:
            registrar_evento("ERROR", "erro_atualizar_historico", {"erro": str(erro)})
            mostrar_mensagem_erro("Nao foi possivel atualizar historico de perguntas.")

        registrar_evento(
            "INFO",
            "sessao_fim",
            {
                "nickname": nickname,
                "modo": "jogo",
                "pontos": resultado.get("pontos", 0),
                "certas": resultado.get("certas", 0),
                "erradas": resultado.get("erradas", 0),
            },
        )

        mostrar_resumo(resultado)
        aguardar_enter("Pressiona Enter para continuar... ")

        quer_rejogar = pedir_confirmacao("Queres jogar novamente? (s/n): ")
        if not quer_rejogar:
            break


def executar_fluxo_campeonato(contexto_app):
    """Executa modo campeonato para dois jogadores (melhor de 3 rondas).

    Args:
        contexto_app (dict): Contexto global da aplicacao.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input e escreve no terminal.
        - Regista eventos de observabilidade.
    """
    iniciar_ecra("Modo Campeonato")
    perguntas = contexto_app["perguntas"]

    jogador_1 = pedir_nickname(
        minimo=LIMITES["nickname_min"],
        maximo=LIMITES["nickname_max"],
    )
    jogador_2 = pedir_nickname(
        minimo=LIMITES["nickname_min"],
        maximo=LIMITES["nickname_max"],
    )

    dificuldades = listar_dificuldades(perguntas)
    dificuldade = escolher_filtro("dificuldade", dificuldades)
    perguntas_filtradas = filtrar_perguntas(
        perguntas=perguntas,
        categoria="todas",
        dificuldade=dificuldade,
    )

    if len(perguntas_filtradas) < NUM_PERGUNTAS_FIXAS:
        mostrar_mensagem_erro(
            "Nao ha perguntas suficientes para campeonato com 10 por ronda nesta dificuldade."
        )
        return

    config_campeonato = configurar_sessao_base(dificuldade)
    registrar_evento(
        "INFO",
        "campeonato_inicio",
        {
            "jogador_1": jogador_1,
            "jogador_2": jogador_2,
            "dificuldade": dificuldade,
            "num_perguntas_ronda": NUM_PERGUNTAS_FIXAS,
        },
    )

    placar = {
        "jogador_1": {"nome": jogador_1, "rondas_ganhas": 0, "pontos_totais": 0},
        "jogador_2": {"nome": jogador_2, "rondas_ganhas": 0, "pontos_totais": 0},
        "detalhes_rondas": [],
        "vencedor": "",
    }
    ids_usadas_torneio = {}

    for numero_ronda in range(1, 4):
        print(f"\n=== Ronda {numero_ronda}/3 ===")
        perguntas_ronda, ids_usadas_torneio = selecionar_perguntas_ronda(
            perguntas=perguntas_filtradas,
            quantidade=NUM_PERGUNTAS_FIXAS,
            ids_usadas_torneio=ids_usadas_torneio,
        )

        print(f"\nRonda para {jogador_1}")
        resultado_1 = executar_sessao_interativa(perguntas_ronda, config_campeonato, jogador_1)

        print(f"\nRonda para {jogador_2}")
        resultado_2 = executar_sessao_interativa(perguntas_ronda, config_campeonato, jogador_2)

        registar_resultado_ronda(
            placar=placar,
            numero_ronda=numero_ronda,
            jogador_1=jogador_1,
            jogador_2=jogador_2,
            resultado_1=resultado_1,
            resultado_2=resultado_2,
        )

        ultimo = placar["detalhes_rondas"][-1]
        print(
            f"Ronda {numero_ronda}: {jogador_1} {ultimo['pontos_jogador_1']} - "
            f"{ultimo['pontos_jogador_2']} {jogador_2}"
        )

    placar["vencedor"] = determinar_vencedor_campeonato(placar)

    registrar_evento(
        "INFO",
        "campeonato_fim",
        {
            "jogador_1": jogador_1,
            "jogador_2": jogador_2,
            "vencedor": placar["vencedor"],
            "rondas_j1": placar["jogador_1"]["rondas_ganhas"],
            "rondas_j2": placar["jogador_2"]["rondas_ganhas"],
        },
    )

    print("\nResultado Campeonato")
    print(
        f"Rondas ganhas - {jogador_1}: {placar['jogador_1']['rondas_ganhas']} | "
        f"{jogador_2}: {placar['jogador_2']['rondas_ganhas']}"
    )
    print(
        f"Pontos totais - {jogador_1}: {placar['jogador_1']['pontos_totais']} | "
        f"{jogador_2}: {placar['jogador_2']['pontos_totais']}"
    )
    print(f"Vencedor: {placar['vencedor']}")
    aguardar_enter("Pressiona Enter para voltar ao menu... ")


def processar_opcao_menu(opcao, contexto_app):
    """Processa opcao selecionada no menu principal.

    Args:
        opcao (int): Opcao numerica escolhida.
        contexto_app (dict): Contexto global da aplicacao.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida.

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
            mostrar_mensagem_erro("Nao foi possivel carregar o Top 10.")
        aguardar_enter("Pressiona Enter para voltar ao menu... ")
    elif opcao == 4:
        executar_fluxo_campeonato(contexto_app)


def ciclo_menu_principal(contexto_app):
    """Executa ciclo principal do menu ate encerramento da app.

    Args:
        contexto_app (dict): Contexto global da aplicacao.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida.

    Side Effects:
        - Le input e escreve no terminal.
    """
    perguntas = contexto_app["perguntas"]

    while True:
        iniciar_ecra("Menu Principal")
        print(f"Perguntas carregadas: {len(perguntas)}")
        mostrar_menu_principal(MENU_PRINCIPAL_OPCOES)
        opcao = ler_opcao_menu(1, len(MENU_PRINCIPAL_OPCOES))
        processar_opcao_menu(opcao, contexto_app)


def executar_aplicacao():
    """Arranca aplicacao com bootstrap e observabilidade.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida por comando global.

    Side Effects:
        - Le ficheiros JSON de dados.
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
            f"Foram ignoradas {invalidas} perguntas invalidas durante a carga."
        )
        aguardar_enter("Pressiona Enter para continuar para o menu... ")

    try:
        ciclo_menu_principal(contexto)
    finally:
        registrar_evento("INFO", "app_fim", {"motivo": "encerramento"})
