"""config.py

Responsabilidade:
    Centralizar constantes e configuracoes base da aplicacao quiz.

Dependencias:
    Nenhuma.

Funcoes publicas:
    Nenhuma (apenas constantes).
"""

CAMINHO_PERGUNTAS = "perguntas.json"
CAMINHO_PONTUACOES = "pontuacoes.json"
CAMINHO_HISTORICO = "historico_perguntas.json"
NUM_PERGUNTAS_FIXAS = 10

MENU_PRINCIPAL_OPCOES = [
    ("1", "Jogar"),
    ("2", "Regras / Ajuda"),
    ("3", "Sair"),
    ("4", "Top 10"),
    ("5", "Campeonato"),
]

LIMITES = {
    "nickname_min": 1,
    "nickname_max": 20,
    "num_perguntas_min": 1,
    "num_perguntas_max": 50,
    "tempo_limite_min": 5,
    "tempo_limite_max": 60,
}

CONFIG_PADRAO = {
    "num_perguntas": 5,
    "categoria": "todas",
    "dificuldade": "todas",
    "tempo_limite": 12,
    "modo_relogio": False,
    "pontuacao_por_dificuldade": False,
    "mostrar_explicacao": "apos_resposta",
}
