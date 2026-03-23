"""campeonato_flow.py

Responsabilidade:
    Orquestrar o fluxo interativo do modo campeonato.

Dependencias:
    - campeonato_service
    - config
    - jogo_flow
    - log_service
    - perguntas_service
    - ui
    - validacao

Contratos de entrada/saida:
    - executar_fluxo_campeonato(contexto_app): executa campeonato completo no terminal.

Funcoes publicas:
    - executar_fluxo_campeonato
"""

from campeonato_service import determinar_vencedor_campeonato, registar_resultado_ronda, selecionar_perguntas_ronda
from config import LIMITES, NUM_PERGUNTAS_FIXAS
from jogo_flow import configurar_sessao_base, escolher_filtro, executar_sessao_interativa
from log_service import registrar_evento
from perguntas_service import filtrar_perguntas, listar_dificuldades
from ui import aguardar_enter, iniciar_ecra, mostrar_mensagem_erro
from validacao import pedir_nickname


def executar_fluxo_campeonato(contexto_app):
    """Executa modo campeonato para dois jogadores (melhor de 3 rondas).

    Args:
        contexto_app (dict): Contexto global da aplicação.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Lê input e escreve no terminal.
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
            "Não há perguntas suficientes para o campeonato com 10 por ronda nesta dificuldade."
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
