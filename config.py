"""config.py

Responsabilidade:
    Centralizar constantes da aplicacao quiz.

Dependencias:
    Nenhuma.

Contratos de entrada/saida:
    - Entradas: nenhuma (constantes estaticas).
    - Saidas: valores reutilizaveis em UI, dominio e infraestrutura.

Funcoes publicas:
    Nenhuma (apenas constantes).
"""

CAMINHO_PERGUNTAS = "perguntas.json"
CAMINHO_PONTUACOES = "pontuacoes.json"
CAMINHO_HISTORICO = "historico_perguntas.json"
CAMINHO_LOG_EVENTOS = "logs_eventos.json"

NUM_PERGUNTAS_FIXAS = 10
TEMPO_LIMITE_FIXO = 20

MENU_PRINCIPAL_OPCOES = [
    ("1", "Jogar"),
    ("2", "Regras / Ajuda"),
    ("3", "Top 10"),
    ("4", "Campeonato"),
]

LIMITES = {
    "nickname_min": 1,
    "nickname_max": 20,
}

CONFIG_PADRAO = {
    "num_perguntas": NUM_PERGUNTAS_FIXAS,
    "categoria": "todas",
    "dificuldade": "todas",
    "tempo_limite": TEMPO_LIMITE_FIXO,
    "modo_relogio": True,
    "pontuacao_por_dificuldade": True,
    "mostrar_explicacao": "apos_resposta",
}
