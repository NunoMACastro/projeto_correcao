"""campeonato_service.py

Responsabilidade:
    Coordenar dominio do modo campeonato (melhor de 3 rondas, 2 jogadores).

Dependencias:
    - jogo_service
    - perguntas_service

Contratos de entrada/saida:
    - jogar_campeonato(...): devolve placar completo sem imprimir no terminal.

Funcoes publicas:
    - selecionar_perguntas_ronda
    - jogar_ronda_campeonato
    - registar_resultado_ronda
    - determinar_vencedor_campeonato
    - jogar_campeonato
"""

from src.domain.jogo_service import jogar_sessao
from src.domain.perguntas_service import selecionar_perguntas_aleatorias


def selecionar_perguntas_ronda(perguntas, quantidade, ids_usadas_torneio):
    """Seleciona perguntas para uma ronda evitando repeticoes do torneio.

    Args:
        perguntas (list[dict]): Universo elegivel do campeonato.
        quantidade (int): Numero de perguntas por ronda.
        ids_usadas_torneio (dict[str, bool]): IDs usadas em rondas anteriores.

    Returns:
        tuple[list[dict], dict[str, bool]]: Perguntas da ronda e mapa de IDs atualizado.

    Raises:
        Nenhum.

    Side Effects:
        - Usa gerador pseudoaleatorio da standard library.
    """
    ronda = selecionar_perguntas_aleatorias(
        perguntas=perguntas,
        quantidade=quantidade,
        ids_evitar=ids_usadas_torneio,
    )
    if len(ronda) < min(max(1, int(quantidade)), len(perguntas)):
        ids_usadas_torneio = {}
        ronda = selecionar_perguntas_aleatorias(
            perguntas=perguntas,
            quantidade=quantidade,
            ids_evitar=ids_usadas_torneio,
        )

    for pergunta in ronda:
        ids_usadas_torneio[str(pergunta.get("id", ""))] = True
    return ronda, ids_usadas_torneio


def jogar_ronda_campeonato(jogador, perguntas_ronda, config, fornecedor_resposta):
    """Executa uma ronda para um jogador no campeonato.

    Args:
        jogador (str): Nome do jogador.
        perguntas_ronda (list[dict]): Perguntas da ronda.
        config (dict): Configuracao ativa da ronda.
        fornecedor_resposta (callable): Callback de resposta interativa.

    Returns:
        dict: Resultado da ronda para o jogador.

    Raises:
        ValueError: Quando callback de resposta e invalido.

    Side Effects:
        - Side effects dependem apenas do callback injetado.
    """
    return jogar_sessao(perguntas_ronda, config, jogador, fornecedor_resposta)


def registar_resultado_ronda(placar, numero_ronda, jogador_1, jogador_2, resultado_1, resultado_2):
    """Atualiza placar com o resultado de uma ronda.

    Args:
        placar (dict): Estrutura acumulada do campeonato.
        numero_ronda (int): Numero da ronda atual.
        jogador_1 (str): Nome do jogador 1.
        jogador_2 (str): Nome do jogador 2.
        resultado_1 (dict): Resultado da ronda para jogador 1.
        resultado_2 (dict): Resultado da ronda para jogador 2.

    Returns:
        dict: Mesmo placar, atualizado in-place.

    Raises:
        Nenhum.

    Side Effects:
        - Mutacao in-place do dicionario `placar`.
    """
    pontos_1 = int(resultado_1.get("pontos", 0))
    pontos_2 = int(resultado_2.get("pontos", 0))

    placar["jogador_1"]["pontos_totais"] += pontos_1
    placar["jogador_2"]["pontos_totais"] += pontos_2

    detalhe = {
        "ronda": int(numero_ronda),
        "pontos_jogador_1": pontos_1,
        "pontos_jogador_2": pontos_2,
        "vencedor_ronda": "empate",
    }

    if pontos_1 > pontos_2:
        placar["jogador_1"]["rondas_ganhas"] += 1
        detalhe["vencedor_ronda"] = jogador_1
    elif pontos_2 > pontos_1:
        placar["jogador_2"]["rondas_ganhas"] += 1
        detalhe["vencedor_ronda"] = jogador_2

    placar["detalhes_rondas"].append(detalhe)
    return placar


def determinar_vencedor_campeonato(placar):
    """Determina vencedor final pelo numero de rondas e depois pontos totais.

    Args:
        placar (dict): Estrutura do campeonato.

    Returns:
        str: Nome do vencedor ou `'empate'`.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
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


def jogar_campeonato(
    perguntas,
    config_base,
    jogador_1,
    jogador_2,
    fornecedor_resposta_j1,
    fornecedor_resposta_j2,
):
    """Executa campeonato completo para dois jogadores.

    Args:
        perguntas (list[dict]): Perguntas disponiveis para o campeonato.
        config_base (dict): Configuracao base da sessao.
        jogador_1 (str): Nome do primeiro jogador.
        jogador_2 (str): Nome do segundo jogador.
        fornecedor_resposta_j1 (callable): Callback de resposta do jogador 1.
        fornecedor_resposta_j2 (callable): Callback de resposta do jogador 2.

    Returns:
        dict: Placar final com detalhes por ronda e vencedor.

    Raises:
        ValueError: Quando callbacks sao invalidos.

    Side Effects:
        - Side effects dependem apenas dos callbacks injetados.
    """
    if not callable(fornecedor_resposta_j1) or not callable(fornecedor_resposta_j2):
        raise ValueError("Callbacks de resposta do campeonato devem ser callables.")

    placar = {
        "jogador_1": {"nome": jogador_1, "rondas_ganhas": 0, "pontos_totais": 0},
        "jogador_2": {"nome": jogador_2, "rondas_ganhas": 0, "pontos_totais": 0},
        "detalhes_rondas": [],
        "vencedor": "",
    }
    quantidade_por_ronda = int(config_base.get("num_perguntas", 3))
    ids_usadas_torneio = {}

    for numero_ronda in range(1, 4):
        perguntas_ronda, ids_usadas_torneio = selecionar_perguntas_ronda(
            perguntas=perguntas,
            quantidade=quantidade_por_ronda,
            ids_usadas_torneio=ids_usadas_torneio,
        )

        resultado_1 = jogar_ronda_campeonato(
            jogador=jogador_1,
            perguntas_ronda=perguntas_ronda,
            config=config_base,
            fornecedor_resposta=fornecedor_resposta_j1,
        )
        resultado_2 = jogar_ronda_campeonato(
            jogador=jogador_2,
            perguntas_ronda=perguntas_ronda,
            config=config_base,
            fornecedor_resposta=fornecedor_resposta_j2,
        )

        registar_resultado_ronda(
            placar=placar,
            numero_ronda=numero_ronda,
            jogador_1=jogador_1,
            jogador_2=jogador_2,
            resultado_1=resultado_1,
            resultado_2=resultado_2,
        )

    placar["vencedor"] = determinar_vencedor_campeonato(placar)
    return placar
