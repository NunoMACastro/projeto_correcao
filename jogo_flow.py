"""jogo_flow.py

Responsabilidade:
    Orquestrar o fluxo interativo do modo jogo (UI + regras + persistência).

Dependencias:
    - time
    - config
    - jogo_service
    - log_service
    - perguntas_service
    - pontuacoes_service
    - ui
    - validacao

Contratos de entrada/saida:
    - executar_fluxo_jogo(contexto_app): executa ciclo completo de jogo com re-jogar.
    - executar_sessao_interativa(...): executa sessão de perguntas com feedback por pergunta.

Funcoes publicas:
    - escolher_filtro
    - configurar_sessao_base
    - executar_sessao_interativa
    - executar_fluxo_jogo
"""

import time

from config import CONFIG_PADRAO, LIMITES, NUM_PERGUNTAS_FIXAS, TEMPO_LIMITE_FIXO
from jogo_service import aplicar_avaliacao_no_estado, avaliar_resposta, finalizar_estado_sessao, iniciar_estado_sessao
from log_service import registrar_evento
from perguntas_service import (
    atualizar_historico_global,
    filtrar_perguntas,
    listar_dificuldades,
    reiniciar_historico_se_necessario,
    selecionar_perguntas_com_historico,
)
from pontuacoes_service import guardar_resultado
from ui import (
    aguardar_enter,
    iniciar_ecra,
    mostrar_mensagem_aviso,
    mostrar_mensagem_erro,
    mostrar_mensagem_info,
    mostrar_mensagem_sucesso,
    mostrar_resumo,
)
from validacao import pedir_confirmacao, pedir_inteiro_intervalo, pedir_nickname


ROTULOS_DIFICULDADE = {
    "facil": "fácil",
    "media": "média",
    "dificil": "difícil",
}


def formatar_opcao_filtro(rotulo, valor):
    """Formata valor de filtro para apresentação ao utilizador.

    Args:
        rotulo (str): Nome do filtro.
        valor (str): Valor interno do filtro.

    Returns:
        str: Valor pronto para exibição na consola.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    valor_str = str(valor)
    if str(rotulo).strip().lower() != "dificuldade":
        return valor_str
    return ROTULOS_DIFICULDADE.get(valor_str.lower(), valor_str)


def escolher_filtro(rotulo, valores):
    """Permite escolher um valor de filtro, incluindo opção `'todas'`.

    Args:
        rotulo (str): Nome legível do filtro.
        valores (list[str]): Valores disponíveis sem `'todas'`.

    Returns:
        str: Valor escolhido.

    Raises:
        SystemExit: Quando utilizador pede saída durante input.

    Side Effects:
        - Escreve no terminal e lê input do utilizador.
    """
    opcoes = ["todas"] + list(valores)
    print(f"\nEscolhe {rotulo}:")
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"{indice}) {formatar_opcao_filtro(rotulo, opcao)}")

    escolha = pedir_inteiro_intervalo(
        prompt="Opção: ",
        minimo=1,
        maximo=len(opcoes),
    )
    return opcoes[escolha - 1]


def configurar_sessao_base(dificuldade):
    """Constrói configuração fixa da sessão conforme contrato atual.

    Args:
        dificuldade (str): Dificuldade selecionada no fluxo atual.

    Returns:
        dict: Configuração final de sessão.

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
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Escreve pergunta/opções no terminal.
        - Lê input do utilizador.
    """
    enunciado = pergunta.get("pergunta", "")
    opcoes = pergunta.get("opcoes", [])

    print(f"\n{enunciado}")
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"{indice}) {opcao}")

    inicio = time.time()
    indice_resposta = pedir_inteiro_intervalo("Resposta: ", 1, len(opcoes)) - 1
    fim = time.time()

    return {
        "indice_resposta": indice_resposta,
        "tempo_resposta_seg": round(fim - inicio, 3),
    }


def mostrar_feedback_pergunta(avaliacao, pergunta):
    """Mostra feedback após responder a uma pergunta.

    Args:
        avaliacao (dict): Resultado unitário da pergunta.
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
        mostrar_mensagem_info(f"Explicação: {pergunta.get('explicacao')}")


def executar_sessao_interativa(perguntas, config, nickname):
    """Executa sessão interativa com avaliação de domínio separada.

    Args:
        perguntas (list[dict]): Perguntas selecionadas para sessão.
        config (dict): Configuração da sessão.
        nickname (str): Nome do jogador.

    Returns:
        dict: Resultado consolidado da sessão.

    Raises:
        ValueError: Em inconsistências de avaliação.
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Lê input e escreve feedback no terminal.
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


def executar_fluxo_jogo(contexto_app):
    """Executa fluxo de jogo normal com re-jogar.

    Args:
        contexto_app (dict): Contexto global da aplicação.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saída.

    Side Effects:
        - Lê input e escreve no terminal.
        - Lê/escreve ficheiros JSON de histórico e pontuações.
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
                "Não há perguntas suficientes para jogar 10 nesta dificuldade. "
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
            mostrar_mensagem_erro("Falha ao preparar o histórico de perguntas.")
            return

        print(f"\nEsta partida terá sempre {NUM_PERGUNTAS_FIXAS} perguntas.")
        print(f"Tempo por pergunta: {TEMPO_LIMITE_FIXO}s | Pontuação por dificuldade: ativa.")

        selecionadas = selecionar_perguntas_com_historico(
            perguntas=perguntas_filtradas,
            quantidade=NUM_PERGUNTAS_FIXAS,
            ids_historico_global=ids_historico_global,
        )
        if not selecionadas:
            mostrar_mensagem_erro("Não foi possível selecionar perguntas.")
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
            mostrar_mensagem_erro("Não foi possível guardar a pontuação.")

        try:
            atualizar_historico_global(resultado.get("ids_usadas_sessao", []))
        except (ValueError, OSError) as erro:
            registrar_evento("ERROR", "erro_atualizar_historico", {"erro": str(erro)})
            mostrar_mensagem_erro("Não foi possível atualizar o histórico de perguntas.")

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
