"""perguntas_service.py

Responsabilidade:
    Carregar, validar, filtrar e selecionar perguntas do quiz.

Dependencias:
    - os
    - random
    - json_store
    - config

Funcoes publicas:
    - carregar_perguntas
    - validar_lista_perguntas
    - validar_pergunta
    - normalizar_indice_resposta
    - listar_categorias
    - listar_dificuldades
    - filtrar_perguntas
    - selecionar_perguntas_aleatorias
    - selecionar_perguntas_com_historico
    - obter_ids_historico_global
    - atualizar_historico_global
    - reiniciar_historico_se_necessario
"""

import os
import random

from config import CAMINHO_HISTORICO, CAMINHO_PERGUNTAS
from json_store import carregar_json, guardar_json


def construir_mapa_ids(ids):
    """Cria um mapa de IDs normalizadas para testes de pertença.

    Args:
        ids (list[str] | dict[str, bool] | None): Colecao de IDs.

    Returns:
        dict[str, bool]: Mapa com IDs como chaves.
    """
    mapa = {}
    if not ids:
        return mapa

    if isinstance(ids, dict):
        for valor in ids.keys():
            mapa[str(valor)] = True
        return mapa

    for valor in ids:
        mapa[str(valor)] = True
    return mapa


def carregar_perguntas(caminho=CAMINHO_PERGUNTAS):
    """Carrega e valida perguntas do ficheiro JSON.

    Args:
        caminho (str): Caminho do ficheiro de perguntas.

    Returns:
        list[dict]: Lista validada de perguntas.

    Raises:
        ValueError: Se a lista estiver vazia ou estrutura invalida.
    """
    if not os.path.exists(caminho):
        raise FileNotFoundError(
            f"Ficheiro de perguntas nao encontrado: '{caminho}'."
        )

    perguntas = carregar_json(caminho, [])
    validar_lista_perguntas(perguntas)
    return perguntas


def validar_lista_perguntas(perguntas):
    """Valida a estrutura global da lista de perguntas.

    Args:
        perguntas (list): Lista de perguntas em memoria.

    Returns:
        None

    Raises:
        ValueError: Se lista for vazia ou itens invalidos.
    """
    if not isinstance(perguntas, list):
        raise ValueError("O JSON de perguntas deve ser uma lista.")
    if not perguntas:
        raise ValueError("Nao existem perguntas disponiveis.")

    for indice, pergunta in enumerate(perguntas):
        validar_pergunta(pergunta, indice)


def validar_pergunta(pergunta, indice=0):
    """Valida os campos minimos de uma pergunta.

    Args:
        pergunta (dict): Registo de pergunta.
        indice (int): Posicao da pergunta para mensagens de erro.

    Returns:
        None

    Raises:
        ValueError: Se faltarem campos obrigatorios.
    """
    if not isinstance(pergunta, dict):
        raise ValueError(f"Pergunta no indice {indice} nao e dicionario.")
    if "pergunta" not in pergunta or not str(pergunta["pergunta"]).strip():
        raise ValueError(f"Pergunta no indice {indice} sem enunciado valido.")
    if "opcoes" not in pergunta or not isinstance(pergunta["opcoes"], list) or len(pergunta["opcoes"]) < 2:
        raise ValueError(f"Pergunta no indice {indice} sem opcoes validas.")
    if "resposta" not in pergunta:
        raise ValueError(f"Pergunta no indice {indice} sem campo 'resposta'.")
    normalizar_indice_resposta(pergunta)


def normalizar_indice_resposta(pergunta):
    """Converte o campo resposta para indice 0-based da opcao correta.

    Args:
        pergunta (dict): Pergunta com campo 'resposta' em int ou str.

    Returns:
        int: Indice correto 0-based.

    Raises:
        ValueError: Se nao for possivel mapear resposta para uma opcao.
    """
    opcoes = pergunta.get("opcoes", [])
    resposta = pergunta.get("resposta")

    if isinstance(resposta, int):
        if 0 <= resposta < len(opcoes):
            return resposta
        if 1 <= resposta <= len(opcoes):
            return resposta - 1
        raise ValueError("Resposta numerica fora do intervalo das opcoes.")

    if isinstance(resposta, str):
        alvo = resposta.strip().lower()
        for indice, opcao in enumerate(opcoes):
            if str(opcao).strip().lower() == alvo:
                return indice
        raise ValueError("Resposta textual nao corresponde a nenhuma opcao.")

    raise ValueError("Campo 'resposta' deve ser int ou str.")


def listar_categorias(perguntas):
    """Lista categorias unicas existentes nas perguntas.

    Args:
        perguntas (list[dict]): Lista de perguntas.

    Returns:
        list[str]: Categorias ordenadas.
    """
    categorias = {}
    for pergunta in perguntas:
        categoria = str(pergunta.get("categoria", "")).strip().lower()
        if categoria:
            categorias[categoria] = True
    return sorted(categorias.keys())


def listar_dificuldades(perguntas):
    """Lista dificuldades unicas existentes nas perguntas.

    Args:
        perguntas (list[dict]): Lista de perguntas.

    Returns:
        list[str]: Dificuldades ordenadas.
    """
    dificuldades = {}
    for pergunta in perguntas:
        dificuldade = str(pergunta.get("dificuldade", "")).strip().lower()
        if dificuldade:
            dificuldades[dificuldade] = True
    return sorted(dificuldades.keys())


def filtrar_perguntas(perguntas, categoria="todas", dificuldade="todas"):
    """Filtra perguntas por categoria e dificuldade.

    Args:
        perguntas (list[dict]): Lista base.
        categoria (str): Categoria alvo ou 'todas'.
        dificuldade (str): Dificuldade alvo ou 'todas'.

    Returns:
        list[dict]: Perguntas filtradas.
    """
    categoria_alvo = categoria.strip().lower()
    dificuldade_alvo = dificuldade.strip().lower()
    filtradas = []

    for pergunta in perguntas:
        categoria_ok = (
            categoria_alvo == "todas"
            or str(pergunta.get("categoria", "")).strip().lower() == categoria_alvo
        )
        dificuldade_ok = (
            dificuldade_alvo == "todas"
            or str(pergunta.get("dificuldade", "")).strip().lower() == dificuldade_alvo
        )
        if categoria_ok and dificuldade_ok:
            filtradas.append(pergunta)

    return filtradas


def selecionar_perguntas_aleatorias(perguntas, quantidade, ids_evitar=None):
    """Seleciona perguntas aleatorias sem repeticao.

    Args:
        perguntas (list[dict]): Universo elegivel.
        quantidade (int): Numero pretendido de perguntas.
        ids_evitar (list[str] | dict[str, bool] | None): IDs a evitar na selecao.

    Returns:
        list[dict]: Perguntas escolhidas.
    """
    ids_bloqueados = construir_mapa_ids(ids_evitar)
    candidatas = [p for p in perguntas if str(p.get("id", "")) not in ids_bloqueados]

    if not candidatas:
        return []

    quantidade_ajustada = min(max(1, quantidade), len(candidatas))
    return random.sample(candidatas, quantidade_ajustada)


def selecionar_perguntas_com_historico(perguntas, quantidade, ids_historico_global):
    """Seleciona perguntas priorizando as ainda nao usadas globalmente.

    Regras:
        1) Primeiro tenta selecionar do conjunto "novo" (fora do historico global).
        2) Se faltar quantidade, completa com perguntas ja usadas.
        3) Nunca repete perguntas na mesma sessao.

    Args:
        perguntas (list[dict]): Universo elegivel apos filtros.
        quantidade (int): Quantidade pretendida.
        ids_historico_global (list[str] | dict[str, bool]): IDs usadas em sessoes anteriores.

    Returns:
        list[dict]: Perguntas escolhidas para a sessao.
    """
    if not perguntas:
        return []

    quantidade_ajustada = min(max(1, quantidade), len(perguntas))
    ids_historico = construir_mapa_ids(ids_historico_global)

    novas = selecionar_perguntas_aleatorias(
        perguntas=perguntas,
        quantidade=quantidade_ajustada,
        ids_evitar=ids_historico,
    )
    if len(novas) >= quantidade_ajustada:
        return novas

    ids_ja_escolhidas = {}
    for pergunta in novas:
        ids_ja_escolhidas[str(pergunta.get("id", ""))] = True
    restantes_necessarias = quantidade_ajustada - len(novas)
    restantes = selecionar_perguntas_aleatorias(
        perguntas=perguntas,
        quantidade=restantes_necessarias,
        ids_evitar=ids_ja_escolhidas,
    )
    return novas + restantes


def obter_ids_historico_global(caminho=CAMINHO_HISTORICO):
    """Le IDs usados globalmente em sessoes anteriores.

    Args:
        caminho (str): Caminho do ficheiro historico.

    Returns:
        list[str]: IDs usados globalmente.
    """
    dados = carregar_json(caminho, {"ids_usadas_global": []})
    ids = dados.get("ids_usadas_global", [])
    mapa_ids = {}
    ids_unicas = []
    for valor in ids:
        id_normalizado = str(valor)
        if id_normalizado not in mapa_ids:
            mapa_ids[id_normalizado] = True
            ids_unicas.append(id_normalizado)
    return ids_unicas


def atualizar_historico_global(ids_novas, caminho=CAMINHO_HISTORICO):
    """Atualiza historico global com novos IDs usados.

    Args:
        ids_novas (list[str] | dict[str, bool]): IDs usadas na sessao atual.
        caminho (str): Caminho do ficheiro historico.

    Returns:
        None
    """
    ids_existentes = obter_ids_historico_global(caminho)
    mapa_ids = construir_mapa_ids(ids_existentes)
    for valor in ids_novas:
        mapa_ids[str(valor)] = True
    guardar_json(caminho, {"ids_usadas_global": sorted(mapa_ids.keys())})


def reiniciar_historico_se_necessario(ids_elegiveis, caminho=CAMINHO_HISTORICO):
    """Reinicia historico quando nao ha perguntas novas no universo elegivel.

    Args:
        ids_elegiveis (list[str] | dict[str, bool]): IDs possiveis na sessao.
        caminho (str): Caminho do ficheiro historico.

    Returns:
        list[str]: Historico possivelmente ajustado.
    """
    mapa_elegiveis = construir_mapa_ids(ids_elegiveis)
    ids_global = obter_ids_historico_global(caminho)
    mapa_global = construir_mapa_ids(ids_global)

    if mapa_elegiveis and all(
        id_elegivel in mapa_global for id_elegivel in mapa_elegiveis
    ):
        ids_filtradas = []
        for id_global in ids_global:
            if id_global not in mapa_elegiveis:
                ids_filtradas.append(id_global)
        ids_global = sorted(ids_filtradas)
        guardar_json(caminho, {"ids_usadas_global": ids_global})

    return ids_global
