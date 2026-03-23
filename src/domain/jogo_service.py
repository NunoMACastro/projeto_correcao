"""jogo_service.py

Responsabilidade:
    Implementar regras de dominio para avaliacao e agregacao de sessoes de jogo.

Dependencias:
    - perguntas_service

Contratos de entrada/saida:
    - jogar_sessao(...): recebe perguntas + config + callback de resposta e devolve resultado final.
    - avaliar_resposta(...): devolve avaliacao de uma unica pergunta sem I/O.

Funcoes publicas:
    - pontuar_resposta
    - calcular_percentagem
    - iniciar_estado_sessao
    - avaliar_resposta
    - aplicar_avaliacao_no_estado
    - finalizar_estado_sessao
    - jogar_sessao
"""

from src.domain.perguntas_service import normalizar_indice_resposta


def pontuar_resposta(correta, dificuldade="facil", usar_pesos=False):
    """Calcula pontos ganhos numa resposta.

    Args:
        correta (bool): Indica se a resposta final conta como correta.
        dificuldade (str): Dificuldade da pergunta.
        usar_pesos (bool): Se True, aplica pesos por dificuldade.

    Returns:
        int: Pontos atribuidos para a pergunta.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    if not correta:
        return 0
    if not usar_pesos:
        return 1

    tabela = {"facil": 1, "media": 2, "dificil": 3}
    return tabela.get(str(dificuldade).strip().lower(), 1)


def calcular_percentagem(certas, total):
    """Calcula percentagem de acertos.

    Args:
        certas (int): Total de respostas corretas.
        total (int): Total de perguntas respondidas.

    Returns:
        float: Percentagem com 2 casas decimais.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    if int(total) <= 0:
        return 0.0
    return round((int(certas) / int(total)) * 100, 2)


def iniciar_estado_sessao(perguntas, config, nickname):
    """Inicializa estado acumulador da sessao.

    Args:
        perguntas (list[dict]): Perguntas selecionadas para a sessao.
        config (dict): Configuracao ativa da sessao.
        nickname (str): Nome do jogador.

    Returns:
        dict: Estado inicial pronto para receber avaliacoes por pergunta.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    return {
        "nickname": nickname,
        "config": dict(config),
        "total_perguntas": len(perguntas),
        "certas": 0,
        "erradas": 0,
        "pontos": 0,
        "ids_usadas_sessao": [],
        "detalhes": [],
    }


def avaliar_resposta(pergunta, indice_resposta, tempo_resposta_seg, config):
    """Avalia resposta de uma pergunta sem realizar I/O.

    Args:
        pergunta (dict): Pergunta atual.
        indice_resposta (int): Indice 0-based escolhido pelo jogador.
        tempo_resposta_seg (float): Tempo decorrido para responder.
        config (dict): Configuracao da sessao.

    Returns:
        dict: Resultado unitario da pergunta.

    Raises:
        ValueError: Se a resposta correta da pergunta for invalida.

    Side Effects:
        Nenhum.
    """
    indice_correto = normalizar_indice_resposta(pergunta)
    correta = int(indice_resposta) == indice_correto

    tempo_limite = int(config.get("tempo_limite", 20))
    modo_relogio = bool(config.get("modo_relogio", False))
    fora_tempo = modo_relogio and float(tempo_resposta_seg) > tempo_limite
    if fora_tempo:
        correta = False

    pontos = pontuar_resposta(
        correta=correta,
        dificuldade=pergunta.get("dificuldade", "facil"),
        usar_pesos=bool(config.get("pontuacao_por_dificuldade", False)),
    )

    return {
        "indice_resposta": int(indice_resposta),
        "indice_correto": indice_correto,
        "respondeu_em_segundos": round(float(tempo_resposta_seg), 3),
        "correta": correta,
        "fora_tempo": fora_tempo,
        "pontos": pontos,
    }


def aplicar_avaliacao_no_estado(estado_sessao, pergunta, avaliacao):
    """Atualiza estado acumulado com o resultado de uma pergunta.

    Args:
        estado_sessao (dict): Estado acumulador da sessao.
        pergunta (dict): Pergunta avaliada.
        avaliacao (dict): Avaliacao devolvida por `avaliar_resposta`.

    Returns:
        dict: Estado atualizado (mesma referencia para encadeamento).

    Raises:
        Nenhum.

    Side Effects:
        - Mutacao in-place do dicionario de estado.
    """
    if avaliacao.get("correta", False):
        estado_sessao["certas"] += 1
    else:
        estado_sessao["erradas"] += 1

    estado_sessao["pontos"] += int(avaliacao.get("pontos", 0))
    estado_sessao["ids_usadas_sessao"].append(str(pergunta.get("id", "")))

    detalhe = {
        "id": str(pergunta.get("id", "")),
        "correta": bool(avaliacao.get("correta", False)),
        "fora_tempo": bool(avaliacao.get("fora_tempo", False)),
        "pontos": int(avaliacao.get("pontos", 0)),
        "respondeu_em_segundos": float(avaliacao.get("respondeu_em_segundos", 0.0)),
    }
    if pergunta.get("explicacao"):
        detalhe["explicacao"] = str(pergunta.get("explicacao", ""))
    estado_sessao["detalhes"].append(detalhe)
    return estado_sessao


def finalizar_estado_sessao(estado_sessao):
    """Consolida estado de sessao num resultado persistivel.

    Args:
        estado_sessao (dict): Estado acumulado da sessao.

    Returns:
        dict: Resultado final da sessao.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    total = int(estado_sessao.get("total_perguntas", 0))
    certas = int(estado_sessao.get("certas", 0))
    config = estado_sessao.get("config", {})
    return {
        "nickname": estado_sessao.get("nickname", "anon"),
        "modo": "relogio" if config.get("modo_relogio", False) else "normal",
        "pontos": int(estado_sessao.get("pontos", 0)),
        "certas": certas,
        "erradas": int(estado_sessao.get("erradas", 0)),
        "percentagem": calcular_percentagem(certas, total),
        "num_perguntas": total,
        "categoria": config.get("categoria", "todas"),
        "dificuldade": config.get("dificuldade", "todas"),
        "ids_usadas_sessao": list(estado_sessao.get("ids_usadas_sessao", [])),
        "detalhes": list(estado_sessao.get("detalhes", [])),
    }


def jogar_sessao(perguntas, config, nickname, fornecedor_resposta):
    """Executa sessao completa com callback externo de recolha de resposta.

    Args:
        perguntas (list[dict]): Perguntas selecionadas para a sessao.
        config (dict): Configuracao da sessao.
        nickname (str): Nome do jogador.
        fornecedor_resposta (callable): Funcao que recebe pergunta e devolve:
            {"indice_resposta": int, "tempo_resposta_seg": float}

    Returns:
        dict: Resultado final da sessao.

    Raises:
        ValueError: Quando o callback de resposta e invalido.

    Side Effects:
        - Side effects dependem apenas do callback injetado.
    """
    if not callable(fornecedor_resposta):
        raise ValueError("fornecedor_resposta deve ser uma funcao callable.")

    estado = iniciar_estado_sessao(perguntas, config, nickname)

    for pergunta in perguntas:
        resposta = fornecedor_resposta(pergunta)
        indice_resposta = int(resposta.get("indice_resposta", -1))
        tempo_resposta_seg = float(resposta.get("tempo_resposta_seg", 0.0))

        avaliacao = avaliar_resposta(
            pergunta=pergunta,
            indice_resposta=indice_resposta,
            tempo_resposta_seg=tempo_resposta_seg,
            config=config,
        )
        aplicar_avaliacao_no_estado(estado, pergunta, avaliacao)

    return finalizar_estado_sessao(estado)
