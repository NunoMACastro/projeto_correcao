"""jogo_service.py

Responsabilidade:
    Executar sessoes de jogo e calcular resultados.

Dependencias:
    - time
    - perguntas_service
    - validacao

Funcoes publicas:
    - pontuar_resposta
    - fazer_pergunta
    - fazer_pergunta_relogio
    - jogar_sessao
    - calcular_percentagem
"""

import time

from perguntas_service import normalizar_indice_resposta
from validacao import pedir_inteiro_intervalo


def pontuar_resposta(correta, dificuldade="facil", usar_pesos=False):
    """Calcula pontos ganhos numa resposta.

    Args:
        correta (bool): Indica se a resposta esta correta.
        dificuldade (str): Dificuldade da pergunta.
        usar_pesos (bool): Se True, aplica pesos por dificuldade.

    Returns:
        int: Pontos atribuídos para a pergunta.
    """
    if not correta:
        return 0
    if not usar_pesos:
        return 1

    tabela = {"facil": 1, "media": 2, "dificil": 3}
    return tabela.get(str(dificuldade).strip().lower(), 1)


def fazer_pergunta(pergunta, config):
    """Mostra pergunta, le resposta e devolve resultado unitario.

    Args:
        pergunta (dict): Pergunta atual.
        config (dict): Configuracao ativa da sessao.

    Returns:
        dict: Resultado da pergunta (correta, pontos, respondeu_em_segundos).
    """
    enunciado = pergunta.get("pergunta", "")
    opcoes = pergunta.get("opcoes", [])
    indice_correto = normalizar_indice_resposta(pergunta)

    print(f"\n{enunciado}")
    for i, opcao in enumerate(opcoes, start=1):
        print(f"{i}) {opcao}")

    inicio = time.time()
    resposta_user = pedir_inteiro_intervalo("Resposta: ", 1, len(opcoes)) - 1
    fim = time.time()

    correta = resposta_user == indice_correto
    pontos = pontuar_resposta(
        correta=correta,
        dificuldade=pergunta.get("dificuldade", "facil"),
        usar_pesos=config.get("pontuacao_por_dificuldade", False),
    )

    return {
        "correta": correta,
        "pontos": pontos,
        "respondeu_em_segundos": round(fim - inicio, 3),
    }


def fazer_pergunta_relogio(pergunta, config):
    """Executa pergunta com limite de tempo por resposta.

    Args:
        pergunta (dict): Pergunta atual.
        config (dict): Configuracao da sessao, incluindo tempo limite.

    Returns:
        dict: Resultado da pergunta com validacao temporal.
    """
    resultado = fazer_pergunta(pergunta, config)
    tempo_limite = int(config.get("tempo_limite", 12))
    fora_tempo = resultado["respondeu_em_segundos"] > tempo_limite
    if fora_tempo:
        resultado["correta"] = False
        resultado["pontos"] = 0
    resultado["fora_tempo"] = fora_tempo
    return resultado


def calcular_percentagem(certas, total):
    """Calcula percentagem de acertos.

    Args:
        certas (int): Total de respostas corretas.
        total (int): Total de perguntas respondidas.

    Returns:
        float: Percentagem com 2 casas decimais.
    """
    if total <= 0:
        return 0.0
    return round((certas / total) * 100, 2)


def jogar_sessao(perguntas, config, nickname):
    """Executa uma sessao completa de jogo.

    Args:
        perguntas (list[dict]): Perguntas selecionadas para a sessao.
        config (dict): Configuracao da sessao.
        nickname (str): Nome do jogador.

    Returns:
        dict: Resultado agregado da sessao.
    """
    certas = 0
    erradas = 0
    pontos = 0
    ids_usadas = []

    for pergunta in perguntas:
        if config.get("modo_relogio", False):
            resultado = fazer_pergunta_relogio(pergunta, config)
        else:
            resultado = fazer_pergunta(pergunta, config)

        if resultado.get("fora_tempo", False):
            erradas += 1
            print("Tempo esgotado. Conta como errada.")
        elif resultado["correta"]:
            certas += 1
            print("Resposta correta.")
        else:
            erradas += 1
            print("Resposta errada.")

        if pergunta.get("explicacao"):
            print(f"Explicacao: {pergunta['explicacao']}")

        pontos += resultado["pontos"]
        ids_usadas.append(str(pergunta.get("id", "")))

    total = len(perguntas)
    return {
        "nickname": nickname,
        "modo": "relogio" if config.get("modo_relogio", False) else "normal",
        "pontos": pontos,
        "certas": certas,
        "erradas": erradas,
        "percentagem": calcular_percentagem(certas, total),
        "num_perguntas": total,
        "categoria": config.get("categoria", "todas"),
        "dificuldade": config.get("dificuldade", "todas"),
        "ids_usadas_sessao": ids_usadas,
    }
