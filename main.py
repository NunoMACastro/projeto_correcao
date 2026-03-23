"""main.py

Responsabilidade:
    Ponto de entrada da aplicacao e ciclo principal de menu.

Dependencias:
    - config
    - campeonato_service
    - menu
    - ui
    - perguntas_service
    - jogo_service
    - pontuacoes_service
    - validacao

Funcoes publicas:
    - iniciar_aplicacao
    - ciclo_menu_principal
    - escolher_filtro
    - configurar_nivel_3
    - executar_modo_jogo
    - executar_modo_campeonato
"""

from config import (
    CONFIG_PADRAO,
    LIMITES,
    MENU_PRINCIPAL_OPCOES,
    NUM_PERGUNTAS_FIXAS,
    TEMPO_LIMITE_FIXO,
)
from campeonato_service import jogar_campeonato
from jogo_service import jogar_sessao
from menu import ler_opcao_menu, mostrar_menu_principal
from pontuacoes_service import guardar_resultado, mostrar_top10
from perguntas_service import (
    atualizar_historico_global,
    carregar_perguntas,
    filtrar_perguntas,
    listar_dificuldades,
    reiniciar_historico_se_necessario,
    selecionar_perguntas_com_historico,
)
from ui import (
    aguardar_enter,
    limpar_ecra,
    mostrar_mensagem_erro,
    mostrar_regras,
    mostrar_resumo,
    mostrar_titulo,
)
from validacao import pedir_confirmacao, pedir_inteiro_intervalo, pedir_nickname


def escolher_filtro(rotulo, valores):
    """Permite escolher um valor de filtro, incluindo opcao 'todas'.

    Args:
        rotulo (str): Nome legivel do filtro.
        valores (list[str]): Valores possiveis (sem 'todas').

    Returns:
        str: Valor escolhido ou 'todas'.
    """
    opcoes = ["todas"] + valores
    print(f"\nEscolhe {rotulo}:")
    for indice, opcao in enumerate(opcoes, start=1):
        print(f"{indice}) {opcao}")

    escolha = pedir_inteiro_intervalo(
        prompt="Opcao: ",
        minimo=1,
        maximo=len(opcoes),
    )
    return opcoes[escolha - 1]


def configurar_nivel_3():
    """Constroi configuracao fixa da sessao para o jogo.

    Returns:
        dict: Configuracao com contra-relogio a 20s e pontuacao por dificuldade.
    """
    config = dict(CONFIG_PADRAO)
    config["modo_relogio"] = True
    config["tempo_limite"] = TEMPO_LIMITE_FIXO
    config["pontuacao_por_dificuldade"] = True
    return config


def executar_modo_jogo(perguntas):
    """Executa o ciclo de jogo MVP, incluindo re-jogar.

    Args:
        perguntas (list[dict]): Perguntas validadas carregadas em memoria.

    Returns:
        None
    """
    limpar_ecra()
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

        ids_elegiveis = [
            str(pergunta.get("id", "")) for pergunta in perguntas_filtradas
        ]
        ids_historico_global = reiniciar_historico_se_necessario(ids_elegiveis)
        print(f"Esta partida tera sempre {NUM_PERGUNTAS_FIXAS} perguntas.")
        print(
            f"Tempo por pergunta: {TEMPO_LIMITE_FIXO}s | "
            "Pontuacao por dificuldade: ativa."
        )
        selecionadas = selecionar_perguntas_com_historico(
            perguntas=perguntas_filtradas,
            quantidade=NUM_PERGUNTAS_FIXAS,
            ids_historico_global=ids_historico_global,
        )
        if not selecionadas:
            mostrar_mensagem_erro("Nao foi possivel selecionar perguntas.")
            return

        config_sessao = configurar_nivel_3()
        config_sessao["num_perguntas"] = NUM_PERGUNTAS_FIXAS
        config_sessao["categoria"] = "todas"
        config_sessao["dificuldade"] = dificuldade
        resultado = jogar_sessao(selecionadas, config_sessao, nickname)
        guardar_resultado(resultado)
        atualizar_historico_global(resultado.get("ids_usadas_sessao", []))
        mostrar_resumo(resultado)
        aguardar_enter("Pressiona Enter para continuar... ")

        quer_rejogar = pedir_confirmacao("Queres jogar novamente? (s/n): ")
        if not quer_rejogar:
            break


def executar_modo_campeonato(perguntas):
    """Executa modo campeonato (melhor de 3 rondas) para dois jogadores.

    Args:
        perguntas (list[dict]): Perguntas validadas carregadas em memoria.

    Returns:
        None
    """
    limpar_ecra()
    print("\nModo Campeonato")
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
            "Nao ha perguntas suficientes para campeonato com 10 por ronda "
            "nesta dificuldade."
        )
        return

    print(f"Cada ronda do campeonato tera {NUM_PERGUNTAS_FIXAS} perguntas.")
    print(
        f"Tempo por pergunta: {TEMPO_LIMITE_FIXO}s | "
        "Pontuacao por dificuldade: ativa."
    )
    config_campeonato = configurar_nivel_3()
    config_campeonato["num_perguntas"] = NUM_PERGUNTAS_FIXAS
    config_campeonato["categoria"] = "todas"
    config_campeonato["dificuldade"] = dificuldade

    placar = jogar_campeonato(
        perguntas=perguntas_filtradas,
        config_base=config_campeonato,
        jogador_1=jogador_1,
        jogador_2=jogador_2,
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


def ciclo_menu_principal(perguntas):
    """Executa ciclo principal do menu ate sair.

    Args:
        perguntas (list[dict]): Perguntas carregadas na inicializacao.

    Returns:
        None
    """
    while True:
        limpar_ecra()
        mostrar_titulo()
        print(f"Perguntas carregadas: {len(perguntas)}")
        mostrar_menu_principal(MENU_PRINCIPAL_OPCOES)
        opcao = ler_opcao_menu(1, len(MENU_PRINCIPAL_OPCOES))

        if opcao == 1:
            executar_modo_jogo(perguntas)
        elif opcao == 2:
            limpar_ecra()
            mostrar_regras()
            aguardar_enter("Pressiona Enter para voltar ao menu... ")
        elif opcao == 3:
            limpar_ecra()
            mostrar_top10()
            aguardar_enter("Pressiona Enter para voltar ao menu... ")
        elif opcao == 4:
            executar_modo_campeonato(perguntas)


def iniciar_aplicacao():
    """Arranca a aplicacao com tratamento de erros de bootstrap.

    Returns:
        None
    """
    try:
        perguntas = carregar_perguntas()
    except (FileNotFoundError, ValueError) as erro:
        mostrar_mensagem_erro(str(erro))
        return

    ciclo_menu_principal(perguntas)


if __name__ == "__main__":
    iniciar_aplicacao()
