"""campeonato_service.py

Responsabilidade:
    Coordenar modo campeonato (melhor de 3 rondas para 2 jogadores).

Dependencias:
    - jogo_service
    - perguntas_service

Funcoes publicas:
    - jogar_campeonato
    - jogar_ronda_campeonato
    - determinar_vencedor_campeonato
"""

from jogo_service import jogar_sessao
from perguntas_service import selecionar_perguntas_aleatorias


def selecionar_perguntas_ronda(perguntas, quantidade, ids_usadas_torneio):
    """Seleciona perguntas para uma ronda evitando repeticoes no torneio.

    Args:
        perguntas (list[dict]): Universo elegivel do campeonato.
        quantidade (int): Numero de perguntas por ronda.
        ids_usadas_torneio (dict[str, bool]): IDs ja usadas em rondas anteriores.

    Returns:
        tuple[list[dict], dict[str, bool]]: Perguntas da ronda e IDs usadas atualizadas.
    """
    ronda = selecionar_perguntas_aleatorias(
        perguntas=perguntas,
        quantidade=quantidade,
        ids_evitar=ids_usadas_torneio,
    )
    if len(ronda) < min(max(1, quantidade), len(perguntas)):
        ids_usadas_torneio = {}
        ronda = selecionar_perguntas_aleatorias(
            perguntas=perguntas,
            quantidade=quantidade,
            ids_evitar=ids_usadas_torneio,
        )

    for pergunta in ronda:
        ids_usadas_torneio[str(pergunta.get("id", ""))] = True
    return ronda, ids_usadas_torneio


def jogar_ronda_campeonato(jogador, perguntas_ronda, config):
    """Executa uma ronda de campeonato para um jogador.

    Args:
        jogador (str): Nome do jogador.
        perguntas_ronda (list[dict]): Perguntas da ronda.
        config (dict): Configuracao ativa.

    Returns:
        dict: Resultado da ronda para o jogador.
    """
    print(f"\nRonda para {jogador}")
    return jogar_sessao(perguntas_ronda, config, jogador)


def determinar_vencedor_campeonato(placar):
    """Determina vencedor final com base no placar de rondas e pontos.

    Args:
        placar (dict): Estrutura com dados de rondas e pontos por jogador.

    Returns:
        str: Nome do vencedor ou 'empate'.
    """
    j1 = placar["jogador_1"]
    j2 = placar["jogador_2"]

    if j1["rondas_ganhas"] > j2["rondas_ganhas"]:
        return j1["nome"]
    if j2["rondas_ganhas"] > j1["rondas_ganhas"]:
        return j2["nome"]

    if j1["pontos_totais"] > j2["pontos_totais"]:
        return j1["nome"]
    if j2["pontos_totais"] > j1["pontos_totais"]:
        return j2["nome"]

    return "empate"


def jogar_campeonato(perguntas, config_base, jogador_1, jogador_2):
    """Executa melhor de 3 rondas para dois jogadores.

    Args:
        perguntas (list[dict]): Perguntas disponiveis.
        config_base (dict): Configuracao base de jogo.
        jogador_1 (str): Nome do primeiro jogador.
        jogador_2 (str): Nome do segundo jogador.

    Returns:
        dict: Placar final do campeonato.
    """
    placar = {
        "jogador_1": {"nome": jogador_1, "rondas_ganhas": 0, "pontos_totais": 0},
        "jogador_2": {"nome": jogador_2, "rondas_ganhas": 0, "pontos_totais": 0},
        "detalhes_rondas": [],
        "vencedor": "",
    }
    quantidade_por_ronda = int(config_base.get("num_perguntas", 3))
    ids_usadas_torneio = {}

    for numero_ronda in range(1, 4):
        print(f"\n=== Ronda {numero_ronda}/3 ===")
        perguntas_ronda, ids_usadas_torneio = selecionar_perguntas_ronda(
            perguntas=perguntas,
            quantidade=quantidade_por_ronda,
            ids_usadas_torneio=ids_usadas_torneio,
        )
        resultado_1 = jogar_ronda_campeonato(jogador_1, perguntas_ronda, config_base)
        resultado_2 = jogar_ronda_campeonato(jogador_2, perguntas_ronda, config_base)

        placar["jogador_1"]["pontos_totais"] += int(resultado_1.get("pontos", 0))
        placar["jogador_2"]["pontos_totais"] += int(resultado_2.get("pontos", 0))
        detalhe = {
            "ronda": numero_ronda,
            "pontos_jogador_1": int(resultado_1.get("pontos", 0)),
            "pontos_jogador_2": int(resultado_2.get("pontos", 0)),
            "vencedor_ronda": "empate",
        }

        if resultado_1.get("pontos", 0) > resultado_2.get("pontos", 0):
            placar["jogador_1"]["rondas_ganhas"] += 1
            detalhe["vencedor_ronda"] = jogador_1
        elif resultado_2.get("pontos", 0) > resultado_1.get("pontos", 0):
            placar["jogador_2"]["rondas_ganhas"] += 1
            detalhe["vencedor_ronda"] = jogador_2
        placar["detalhes_rondas"].append(detalhe)
        print(
            f"Ronda {numero_ronda}: {jogador_1} {detalhe['pontos_jogador_1']} - "
            f"{detalhe['pontos_jogador_2']} {jogador_2}"
        )

    placar["vencedor"] = determinar_vencedor_campeonato(placar)
    return placar
