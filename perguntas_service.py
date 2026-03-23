"""perguntas_service.py

Responsabilidade:
    Carregar, validar, filtrar e selecionar perguntas do quiz.

Dependencias:
    - os
    - random
    - config
    - json_store

Contratos de entrada/saida:
    - carregar_perguntas_com_relatorio: devolve perguntas validas e invalidas.
    - carregar_perguntas: devolve apenas perguntas validas prontas para jogo.

Funcoes publicas:
    - carregar_perguntas
    - carregar_perguntas_com_relatorio
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

from config import CAMINHO_HISTORICO, CAMINHO_PERGUNTAS, NUM_PERGUNTAS_FIXAS
from json_store import carregar_json, guardar_json


DIFICULDADES_VALIDAS = {"facil": True, "media": True, "dificil": True}


def construir_mapa_ids(ids):
    """Cria mapa de IDs normalizadas para pesquisas O(1).

    Args:
        ids (list[str] | dict[str, bool] | None): Colecao de IDs.

    Returns:
        dict[str, bool]: Mapa com IDs como chaves.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
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


def _id_pergunta(pergunta):
    """Extrai ID de pergunta como string limpa.

    Args:
        pergunta (dict): Registo de pergunta.

    Returns:
        str: ID normalizado ou string vazia.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    if not isinstance(pergunta, dict):
        return ""
    return str(pergunta.get("id", "")).strip()


def _erro_validacao(indice, pergunta_id, campo, motivo):
    """Constroi mensagem de validacao detalhada.

    Args:
        indice (int): Posicao da pergunta no dataset.
        pergunta_id (str): ID da pergunta quando disponivel.
        campo (str): Campo invalido.
        motivo (str): Motivo tecnico da invalidade.

    Returns:
        str: Mensagem de erro completa.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    id_legivel = pergunta_id or "sem_id"
    return (
        f"Pergunta inválida (índice={indice}, id={id_legivel}, "
        f"campo={campo}): {motivo}."
    )


def validar_lista_perguntas(perguntas):
    """Valida estrutura global da lista de perguntas.

    Args:
        perguntas (list): Lista de perguntas carregada do JSON.

    Returns:
        None

    Raises:
        ValueError: Se o JSON nao for lista ou estiver vazio.

    Side Effects:
        Nenhum.
    """
    if not isinstance(perguntas, list):
        raise ValueError("O ficheiro de perguntas deve conter uma lista JSON.")
    if not perguntas:
        raise ValueError("O ficheiro de perguntas não contém entradas.")


def validar_pergunta(pergunta, indice=0, ids_vistos=None):
    """Valida uma pergunta individual.

    Args:
        pergunta (dict): Registo da pergunta.
        indice (int): Posicao da pergunta para diagnostico.
        ids_vistos (dict[str, bool] | None): Mapa opcional para detetar IDs duplicados.

    Returns:
        None

    Raises:
        ValueError: Quando qualquer campo obrigatorio e invalido.

    Side Effects:
        - Pode atualizar o mapa `ids_vistos` com novo ID valido.
    """
    if not isinstance(pergunta, dict):
        raise ValueError(_erro_validacao(indice, "", "estrutura", "não é dicionário"))

    pergunta_id = _id_pergunta(pergunta)
    if not pergunta_id:
        raise ValueError(_erro_validacao(indice, "", "id", "id em falta ou vazio"))

    if ids_vistos is not None and pergunta_id in ids_vistos:
        raise ValueError(
            _erro_validacao(indice, pergunta_id, "id", "id duplicado no dataset")
        )

    enunciado = str(pergunta.get("pergunta", "")).strip()
    if not enunciado:
        raise ValueError(
            _erro_validacao(indice, pergunta_id, "pergunta", "enunciado vazio")
        )

    opcoes = pergunta.get("opcoes")
    if not isinstance(opcoes, list) or len(opcoes) < 2:
        raise ValueError(
            _erro_validacao(
                indice,
                pergunta_id,
                "opcoes",
                "deve ser lista com pelo menos 2 opções",
            )
        )

    for posicao, opcao in enumerate(opcoes):
        if not str(opcao).strip():
            raise ValueError(
                _erro_validacao(
                    indice,
                    pergunta_id,
                    "opcoes",
                    f"opção na posição {posicao} está vazia",
                )
            )

    if "resposta" not in pergunta:
        raise ValueError(
            _erro_validacao(indice, pergunta_id, "resposta", "campo obrigatorio em falta")
        )

    normalizar_indice_resposta(pergunta)

    categoria = str(pergunta.get("categoria", "")).strip().lower()
    if not categoria:
        raise ValueError(
            _erro_validacao(indice, pergunta_id, "categoria", "categoria em falta ou vazia")
        )

    dificuldade = str(pergunta.get("dificuldade", "")).strip().lower()
    if dificuldade not in DIFICULDADES_VALIDAS:
        raise ValueError(
            _erro_validacao(
                indice,
                pergunta_id,
                "dificuldade",
                "deve ser 'facil', 'media' ou 'dificil' (sem acentos)",
            )
        )

    if ids_vistos is not None:
        ids_vistos[pergunta_id] = True


def normalizar_indice_resposta(pergunta):
    """Converte `resposta` para indice 0-based da opcao correta.

    Args:
        pergunta (dict): Pergunta com campos `opcoes` e `resposta`.

    Returns:
        int: Indice correto 0-based.

    Raises:
        ValueError: Quando nao e possivel mapear resposta para uma opcao valida.

    Side Effects:
        Nenhum.
    """
    opcoes = pergunta.get("opcoes", [])
    resposta = pergunta.get("resposta")

    if not isinstance(opcoes, list) or not opcoes:
        raise ValueError("Campo 'opcoes' inválido para normalizar resposta.")

    if isinstance(resposta, int):
        if 0 <= resposta < len(opcoes):
            return resposta
        if 1 <= resposta <= len(opcoes):
            return resposta - 1
        raise ValueError("Resposta numérica fora do intervalo das opções.")

    if isinstance(resposta, str):
        alvo = resposta.strip().lower()
        for indice, opcao in enumerate(opcoes):
            if str(opcao).strip().lower() == alvo:
                return indice
        raise ValueError("Resposta textual não corresponde a nenhuma opção.")

    raise ValueError("Campo 'resposta' deve ser int ou str.")


def carregar_perguntas_com_relatorio(caminho=CAMINHO_PERGUNTAS, minimo_validas=NUM_PERGUNTAS_FIXAS):
    """Carrega perguntas e devolve relatorio com validas e invalidas.

    Politica tolerante:
        - Perguntas invalidas sao ignoradas e reportadas.
        - A aplicacao falha apenas se o total valido ficar abaixo do minimo.

    Args:
        caminho (str): Caminho do ficheiro de perguntas.
        minimo_validas (int): Minimo de perguntas validas para permitir jogo.

    Returns:
        dict: Estrutura com chaves `validas`, `invalidas` e `total`.

    Raises:
        FileNotFoundError: Quando o ficheiro nao existe.
        ValueError: Quando o conteudo global e invalido ou validas < minimo.

    Side Effects:
        - Le ficheiro JSON de perguntas.
    """
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Ficheiro de perguntas não encontrado: '{caminho}'.")

    perguntas_raw = carregar_json(caminho, [])
    validar_lista_perguntas(perguntas_raw)

    ids_vistos = {}
    validas = []
    invalidas = []

    for indice, pergunta in enumerate(perguntas_raw):
        try:
            validar_pergunta(pergunta, indice=indice, ids_vistos=ids_vistos)
            validas.append(pergunta)
        except ValueError as erro:
            invalidas.append(
                {
                    "indice": indice,
                    "id": _id_pergunta(pergunta),
                    "erro": str(erro),
                }
            )

    if len(validas) < int(minimo_validas):
        raise ValueError(
            "Perguntas válidas insuficientes para jogar: "
            f"{len(validas)} válidas de {len(perguntas_raw)} totais "
            f"(mínimo exigido: {minimo_validas})."
        )

    return {
        "validas": validas,
        "invalidas": invalidas,
        "total": len(perguntas_raw),
    }


def carregar_perguntas(caminho=CAMINHO_PERGUNTAS):
    """Carrega perguntas validas prontas para jogo.

    Args:
        caminho (str): Caminho do ficheiro de perguntas.

    Returns:
        list[dict]: Lista de perguntas validas.

    Raises:
        FileNotFoundError: Quando o ficheiro nao existe.
        ValueError: Quando dados nao suportam iniciar jogo.

    Side Effects:
        - Le ficheiro JSON de perguntas.
    """
    relatorio = carregar_perguntas_com_relatorio(caminho=caminho)
    return relatorio["validas"]


def listar_categorias(perguntas):
    """Lista categorias unicas existentes nas perguntas.

    Args:
        perguntas (list[dict]): Lista de perguntas validas.

    Returns:
        list[str]: Categorias ordenadas alfabeticamente.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
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
        perguntas (list[dict]): Lista de perguntas validas.

    Returns:
        list[str]: Dificuldades ordenadas alfabeticamente.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
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
        perguntas (list[dict]): Lista base de perguntas.
        categoria (str): Categoria alvo ou 'todas'.
        dificuldade (str): Dificuldade alvo ou 'todas'.

    Returns:
        list[dict]: Perguntas filtradas.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    categoria_alvo = str(categoria).strip().lower()
    dificuldade_alvo = str(dificuldade).strip().lower()
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
        ids_evitar (list[str] | dict[str, bool] | None): IDs a excluir.

    Returns:
        list[dict]: Perguntas escolhidas.

    Raises:
        Nenhum.

    Side Effects:
        - Usa gerador pseudoaleatorio da standard library.
    """
    ids_bloqueados = construir_mapa_ids(ids_evitar)
    candidatas = [p for p in perguntas if str(p.get("id", "")) not in ids_bloqueados]

    if not candidatas:
        return []

    quantidade_ajustada = min(max(1, int(quantidade)), len(candidatas))
    return random.sample(candidatas, quantidade_ajustada)


def selecionar_perguntas_com_historico(perguntas, quantidade, ids_historico_global):
    """Seleciona perguntas priorizando as ainda nao usadas globalmente.

    Regras:
        1) Primeiro tenta selecionar perguntas fora do historico global.
        2) Se faltar quantidade, completa com perguntas ja usadas.
        3) Nunca repete perguntas na mesma sessao.

    Args:
        perguntas (list[dict]): Universo elegivel apos filtros.
        quantidade (int): Quantidade pretendida para a sessao.
        ids_historico_global (list[str] | dict[str, bool]): IDs usadas anteriormente.

    Returns:
        list[dict]: Perguntas escolhidas para a sessao.

    Raises:
        Nenhum.

    Side Effects:
        - Usa gerador pseudoaleatorio da standard library.
    """
    if not perguntas:
        return []

    quantidade_ajustada = min(max(1, int(quantidade)), len(perguntas))
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
    """Le IDs usadas globalmente em sessoes anteriores.

    Args:
        caminho (str): Caminho do ficheiro de historico global.

    Returns:
        list[str]: IDs unicas ja usadas.

    Raises:
        ValueError: Quando o JSON esta invalido no caminho.

    Side Effects:
        - Le ficheiro JSON de historico.
    """
    dados = carregar_json(caminho, {"ids_usadas_global": []})
    ids = dados.get("ids_usadas_global", []) if isinstance(dados, dict) else []

    mapa_ids = {}
    ids_unicas = []
    for valor in ids:
        id_normalizado = str(valor)
        if id_normalizado not in mapa_ids:
            mapa_ids[id_normalizado] = True
            ids_unicas.append(id_normalizado)
    return ids_unicas


def atualizar_historico_global(ids_novas, caminho=CAMINHO_HISTORICO):
    """Atualiza historico global com IDs usadas na sessao atual.

    Args:
        ids_novas (list[str] | dict[str, bool]): IDs da sessao atual.
        caminho (str): Caminho do ficheiro de historico.

    Returns:
        None

    Raises:
        OSError: Em falhas de escrita do ficheiro.
        ValueError: Em falhas de leitura do ficheiro existente.

    Side Effects:
        - Le e escreve ficheiro JSON de historico global.
    """
    ids_existentes = obter_ids_historico_global(caminho)
    mapa_ids = construir_mapa_ids(ids_existentes)
    for valor in ids_novas:
        mapa_ids[str(valor)] = True
    guardar_json(caminho, {"ids_usadas_global": sorted(mapa_ids.keys())})


def reiniciar_historico_se_necessario(ids_elegiveis, caminho=CAMINHO_HISTORICO):
    """Reinicia historico quando nao existem perguntas novas no universo elegivel.

    Args:
        ids_elegiveis (list[str] | dict[str, bool]): IDs possiveis para a sessao.
        caminho (str): Caminho do ficheiro de historico global.

    Returns:
        list[str]: Historico global possivelmente ajustado.

    Raises:
        OSError: Em falhas de escrita.
        ValueError: Em falhas de leitura do JSON existente.

    Side Effects:
        - Pode reescrever ficheiro de historico global.
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
