"""config.py

Responsabilidade:
    Centralizar constantes da aplicacao quiz.

Dependencias:
    - pathlib

Contratos de entrada/saida:
    - Entradas: nenhuma (constantes estaticas).
    - Saidas: valores reutilizaveis em UI, dominio e infraestrutura.

Funcoes publicas:
    Nenhuma (apenas constantes).
"""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

CAMINHO_PERGUNTAS = str(DATA_DIR / "perguntas.json")
CAMINHO_PONTUACOES = str(DATA_DIR / "pontuacoes.json")
CAMINHO_HISTORICO = str(DATA_DIR / "historico_perguntas.json")
CAMINHO_LOG_EVENTOS = str(DATA_DIR / "logs_eventos.json")

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
